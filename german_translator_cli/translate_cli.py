#!/usr/bin/env python
# translate_cli.py

import argparse
from transformers import pipeline, M2M100ForConditionalGeneration, M2M100Tokenizer
import logging
import sys
from typing import Generator, Dict, Optional
import yaml
import os

# Constants for configuration paths
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/translator/config.yaml")
PROJECT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

# Available model providers and their base configurations
MODEL_PROVIDERS = {
    "helsinki": {
        "name": "Helsinki-NLP",
        "base_model": "opus-mt-{source}-{target}",
        "base_path": "Helsinki-NLP/opus-mt-{source}-{target}",
    },
    "facebook": {
        "name": "Facebook",
        "base_model": "m2m100",
        "base_path": "facebook/m2m100-{size}",
        "sizes": ["418M", "1.2B"],
    },
    "google": {
        "name": "Google",
        "base_model": "mt5",
        "base_path": "google/mt5-{size}",
        "sizes": ["small", "base", "large"],
    }
}

# Initial basic logging config - will be overridden by command line args
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("transformers").setLevel(logging.ERROR)


def load_config():
    """Load configuration from both user and project config files."""
    config = {}
    
    # Try loading user config
    if os.path.exists(DEFAULT_CONFIG_PATH):
        try:
            with open(DEFAULT_CONFIG_PATH, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                config.update(user_config)
            logging.debug(f"Loaded user config from: {DEFAULT_CONFIG_PATH}")
        except (yaml.YAMLError, FileNotFoundError) as e:
            logging.warning(f"Error loading user config from {DEFAULT_CONFIG_PATH}: {e}")
    
    # Try loading project config (overrides user config)
    if os.path.exists(PROJECT_CONFIG_PATH):
        try:
            with open(PROJECT_CONFIG_PATH, 'r') as f:
                project_config = yaml.safe_load(f) or {}
                config.update(project_config)
            logging.debug(f"Loaded project config from: {PROJECT_CONFIG_PATH}")
        except (yaml.YAMLError, FileNotFoundError) as e:
            logging.warning(f"Error loading project config from {PROJECT_CONFIG_PATH}: {e}")
    
    return config


def get_model_name(provider: str, source_lang: str, target_lang: str, size: Optional[str] = None) -> str:
    """Construct the appropriate model name based on the provider and languages."""
    if provider not in MODEL_PROVIDERS:
        raise ValueError(f"Unknown model provider: {provider}")
    
    provider_config = MODEL_PROVIDERS[provider]
    
    if provider == "helsinki":
        return f"{provider_config['name']}/{provider_config['base_model']}".format(
            source=source_lang, target=target_lang
        )
    elif provider in ["facebook", "google"]:
        if not size:
            size = provider_config['sizes'][0]  # Use smallest size by default
        elif size not in provider_config['sizes']:
            raise ValueError(f"Invalid size for {provider}: {size}. Available sizes: {provider_config['sizes']}")
        return provider_config['base_path'].format(size=size)
    
    raise ValueError(f"Provider {provider} not properly configured")


def read_in_chunks(file_path: str, chunk_size: int = 2048) -> Generator[str, None, None]:
    """Reads a file and yields chunks of a specified size, trying to respect line breaks."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            buffer = ''
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                buffer += chunk
                last_newline = buffer.rfind('\n')
                if last_newline != -1:
                    yield buffer[:last_newline + 1]
                    buffer = buffer[last_newline + 1:]
                elif len(buffer) > 2 * chunk_size:  # Avoid very long lines in buffer
                    yield buffer[:chunk_size]
                    buffer = buffer[chunk_size:]
            yield buffer  # Yield any remaining text
    except (FileNotFoundError, PermissionError, IOError, UnicodeDecodeError) as e:
        logging.error(f"Failed to read input file '{file_path}': {e}")
        sys.exit(1)


def initialize_translator(model_name: str, provider: str, source_lang: str, target_lang: str) -> pipeline:
    """Initialize the appropriate translation pipeline based on the provider."""
    if provider == "facebook":
        model = M2M100ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        tokenizer.src_lang = source_lang
        return pipeline("translation", model=model, tokenizer=tokenizer, device="cpu")
    else:
        return pipeline(
            "translation",
            model=model_name,
            device="cpu",
        )


def translate_text(
    text: str,
    source_lang: str = "de",
    target_lang: str = "en",
    model_name: str = None,
    provider: str = "helsinki",
    model_size: str = None,
    max_length: int = 512
) -> str:
    try:
        from huggingface_hub import snapshot_download, model_info
        import os

        # Construct model name if not provided
        if not model_name:
            try:
                model_name = get_model_name(provider, source_lang, target_lang, model_size)
            except ValueError as e:
                logging.error(str(e))
                return None
            
        logging.debug(f"Constructed model name: {model_name}")
        logging.info(f"Loading translation model: {model_name}...")

        # Verify model exists on Hugging Face Hub
        try:
            info = model_info(model_name)
            logging.debug(f"Model info retrieved: {info}")
            if not info:
                raise ValueError(f"Model '{model_name}' not found on Hugging Face Hub")
        except Exception as e:
            logging.error(f"Failed to verify model '{model_name}': {e}")
            logging.error(f"The language pair {source_lang}->{target_lang} might not be supported.")
            logging.error(f"Available providers: {', '.join(MODEL_PROVIDERS.keys())}")
            return None

        # Configure model caching and download settings
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        logging.debug(f"Using cache directory: {cache_dir}")
        os.makedirs(cache_dir, exist_ok=True)

        try:
            model_path = snapshot_download(
                repo_id=model_name,
                cache_dir=cache_dir,
                local_files_only=False,
                token=None,
            )
            logging.debug(f"Model downloaded to: {model_path}")
        except Exception as e:
            logging.error(f"Failed to download model '{model_name}': {e}")
            logging.error("Please check if the model name is correct and accessible.")
            return None

        # Initialize the appropriate translation pipeline
        translator = initialize_translator(model_path, provider, source_lang, target_lang)

        logging.info("Model loaded. Starting translation...")
        logging.debug(f"Translating text with max length: {max_length}")

        # Perform translation with configurable max_length
        if provider == "facebook":
            results = translator(text, max_length=max_length, src_lang=source_lang, tgt_lang=target_lang)
        else:
            results = translator(text, max_length=max_length)

        if results and isinstance(results, list) and "translation_text" in results[0]:
            translated_text = results[0]["translation_text"]
            logging.info("Translation successful.")
            logging.debug(f"Translated text: '{translated_text}'")
            return translated_text
        else:
            logging.error(f"Translation failed. Unexpected result format: {results}")
            return None

    except ImportError as e:
        logging.error(f"ImportError: {e}. Make sure required packages are installed.")
        logging.error("Try running: pip install torch transformers sacremoses protobuf huggingface_hub")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred during translation: {e}")
        return None


def main():
    # Load configuration first
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Universal text translator supporting multiple model providers."
    )
    group = parser.add_mutually_exclusive_group(
        required=False
    )
    group.add_argument(
        "--text", type=str, help="Text to translate (direct input)."
    )
    group.add_argument(
        "-i", "--input", type=str, help="Path to input file containing text to translate."
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Path to output file for translation."
    )
    parser.add_argument(
        "-s", "--source-lang",
        type=str,
        default=config.get("default_source_lang", "de"),
        help="Source language code (default: from config or de)"
    )
    parser.add_argument(
        "-t", "--target-lang",
        type=str,
        default=config.get("default_target_lang", "en"),
        help="Target language code (default: from config or en)"
    )
    parser.add_argument(
        "-m", "--model", 
        type=str,
        default=config.get("default_model", None),
        help="Optional: Specific Hugging Face model name to use. If provided, overrides provider settings."
    )
    parser.add_argument(
        "-p", "--provider",
        type=str,
        choices=list(MODEL_PROVIDERS.keys()),
        default=config.get("default_provider", "helsinki"),
        help=f"Model provider to use. Available: {', '.join(MODEL_PROVIDERS.keys())}"
    )
    parser.add_argument(
        "--model-size",
        type=str,
        help="Model size for providers that support it (facebook, google)"
    )
    parser.add_argument(
        "-l", "--max-length",
        type=int,
        default=config.get("max_length", 512),
        help="Maximum sequence length for translation (default: from config or 512)"
    )
    parser.add_argument(
        "--log-level",
        type=str.upper,
        default=config.get("log_level", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    parser.add_argument(
        "--log-format",
        type=str,
        default=config.get("log_format", "%(asctime)s - %(levelname)s - %(message)s"),
        help="Specify the log message format (Python logging format)"
    )
    args = parser.parse_args()

    # Configure logging based on command-line arguments or config
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format=args.log_format,
        force=True
    )
    logging.getLogger("transformers").setLevel(logging.ERROR)

    # Log configuration and settings
    logging.debug("Starting translation process with configuration:")
    logging.debug(f"Source language: {args.source_lang}")
    logging.debug(f"Target language: {args.target_lang}")
    logging.debug(f"Provider: {args.provider}")
    logging.debug(f"Model: {args.model if args.model else 'auto'}")
    logging.debug(f"Model size: {args.model_size if args.model_size else 'default'}")
    logging.debug(f"Max length: {args.max_length}")
    logging.debug(f"Using config from: {DEFAULT_CONFIG_PATH if os.path.exists(DEFAULT_CONFIG_PATH) else 'default values'}")

    # Input handling
    if args.input:
        try:
            with open(args.output, "w", encoding="utf-8") as outfile:
                for chunk in read_in_chunks(args.input, chunk_size=1024):
                    translated_text = translate_text(
                        chunk,
                        source_lang=args.source_lang,
                        target_lang=args.target_lang,
                        model_name=args.model,
                        provider=args.provider,
                        model_size=args.model_size,
                        max_length=args.max_length
                    )
                    if translated_text:
                        outfile.write(translated_text)
                    else:
                        logging.error(f"Translation failed for a chunk. Processing stopped.")
                        sys.exit(1)
            logging.info(f"Translation of '{args.input}' complete. Output written to '{args.output}'.")

        except FileNotFoundError:
            logging.error(f"Input file '{args.input}' not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"An error occurred during file processing: {e}")
            sys.exit(1)

    elif args.text:
        translated_text = translate_text(
            args.text,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            model_name=args.model,
            provider=args.provider,
            model_size=args.model_size,
            max_length=args.max_length
        )
        if translated_text:
            if args.output:
                try:
                    with open(args.output, "w", encoding="utf-8") as outfile:
                        outfile.write(translated_text)
                    logging.info(f"Translation written to '{args.output}'.")
                except Exception as e:
                    logging.error(f"Error writing to output file: {e}")
            else:
                print(translated_text)
        else:
            print("Translation failed.", file=sys.stderr)
            sys.exit(1)

    else:
        print("No input text or file specified. Use --text or -i.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
