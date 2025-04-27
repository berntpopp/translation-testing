#!/usr/bin/env python
# translate_cli.py

import argparse
from transformers import pipeline
import logging
import sys
from typing import Generator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Suppress excessive logging from underlying libraries if desired
logging.getLogger("transformers").setLevel(logging.ERROR)

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


def translate_text(
    text: str,
    source_lang: str = "de",
    target_lang: str = "en",
    model_name: str = None,
    max_length: int = 512
) -> str:
    """
    Translates text between specified languages using a Hugging Face model.

    Args:
        text: The source text string to translate.
        source_lang: The source language code (default: "de").
        target_lang: The target language code (default: "en").
        model_name: Optional specific model name to use. If None, will construct using language pairs.
        max_length: Maximum sequence length for translation.

    Returns:
        The translated text string, or None if translation fails.
    """
    try:
        from huggingface_hub import snapshot_download, model_info
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import os

        # Construct model name if not provided
        if not model_name:
            model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
            
        logging.info(f"Loading translation model: {model_name}...")

        # Verify model exists on Hugging Face Hub
        try:
            info = model_info(model_name)
            if not info:
                raise ValueError(f"Model '{model_name}' not found on Hugging Face Hub")
        except Exception as e:
            logging.error(f"Failed to verify model '{model_name}': {e}")
            logging.error(f"The language pair {source_lang}->{target_lang} might not be supported.")
            logging.error("Try checking available models at: https://huggingface.co/Helsinki-NLP")
            return None

        # Configure model caching and download settings
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        os.makedirs(cache_dir, exist_ok=True)

        try:
            model_path = snapshot_download(
                repo_id=model_name,
                cache_dir=cache_dir,
                local_files_only=False,
                token=None,
            )
        except Exception as e:
            logging.error(f"Failed to download model '{model_name}': {e}")
            logging.error("Please check if the model name is correct and accessible.")
            return None

        # Initialize the pipeline with the downloaded model
        translator = pipeline(
            "translation",
            model=model_path,
            tokenizer=model_path,
            device="cpu",
        )

        logging.info("Model loaded. Starting translation...")

        # Perform translation with configurable max_length
        results = translator(text, max_length=max_length)

        if results and isinstance(results, list) and "translation_text" in results[0]:
            translated_text = results[0]["translation_text"]
            logging.info("Translation successful.")
            return translated_text
        else:
            logging.error(f"Translation failed. Unexpected result format: {results}")
            return None

    except ImportError as e:
        logging.error(f"ImportError: {e}. Make sure required packages are installed.")
        logging.error("Try running: pip install torch transformers hf_xet huggingface_hub")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred during translation: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Universal text translator using Helsinki-NLP models."
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
        default="de",
        help="Source language code (default: de)"
    )
    parser.add_argument(
        "-t", "--target-lang",
        type=str,
        default="en",
        help="Target language code (default: en)"
    )
    parser.add_argument(
        "-m", "--model", 
        type=str,
        help="Optional: Specific Hugging Face model name to use. If provided, overrides source/target language options."
    )
    parser.add_argument(
        "-l", "--max-length",
        type=int,
        default=512,
        help="Maximum sequence length for translation (default: 512)"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Input handling
    if args.input:
        try:
            with open(args.output, "w", encoding="utf-8") as outfile:
                for chunk in read_in_chunks(args.input, chunk_size=1024):  # Adjust chunk_size as needed
                    translated_text = translate_text(
                        chunk,
                        source_lang=args.source_lang,
                        target_lang=args.target_lang,
                        model_name=args.model,
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
            print("Translation failed.", file=sys.stderr)
            sys.exit(1)

    else:
        print("No input text or file specified. Use --text or -i.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
