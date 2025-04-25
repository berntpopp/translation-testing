#!/usr/bin/env python
# translate_cli.py

import argparse
from transformers import pipeline
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Suppress excessive logging from underlying libraries if desired
logging.getLogger("transformers").setLevel(logging.ERROR)


def translate_text(german_text: str, model_name: str = "Helsinki-NLP/opus-mt-de-en") -> str:
    """
    Translates German text to English using a specified Hugging Face model.

    Args:
        german_text: The German text string to translate.
        model_name: The name of the Hugging Face translation model to use.

    Returns:
        The translated English text string, or None if translation fails.
    """
    try:
        from huggingface_hub import snapshot_download
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import os

        logging.info(f"Loading translation model: {model_name}...")
        
        # Configure model caching and download settings
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Use snapshot_download for faster downloads with XET storage
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,  # Set to True if you want to use only cached files
            token=None  # Add your HF token here if you have one for faster downloads
        )
        
        # Initialize the pipeline with the downloaded model
        translator = pipeline(
            "translation_de_to_en",
            model=model_path,
            tokenizer=model_path,
            device="cpu"  # Explicitly set device to avoid CUDA warnings if no GPU
        )
        
        logging.info("Model loaded. Starting translation...")

        # Perform translation. Adjust max_length if needed for longer texts.
        results = translator(german_text, max_length=512)

        if results and isinstance(results, list) and 'translation_text' in results[0]:
            translated_text = results[0]['translation_text']
            logging.info("Translation successful.")
            return translated_text
        else:
            logging.error(f"Translation failed. Unexpected result format: {results}")
            return None

    except ImportError as e:
        logging.error(f"ImportError: {e}. Make sure required packages are installed.")
        logging.error("Try running: pip install torch transformers hf_xet")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred during translation: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="German-to-English translation CLI tool.")
    group = parser.add_mutually_exclusive_group(required=False)  # Changed to not required
    group.add_argument('--text', type=str, help='German text to translate (direct input).')
    group.add_argument('-i', '--input', type=str, help='Path to input file containing German text.')
    parser.add_argument('-o', '--output', type=str, help='Path to output file for English translation.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Input handling
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                german_input = f.read()
            logging.info(f"Read input from file: {args.input}")
            input_source = "file"
        except (FileNotFoundError, PermissionError, IOError, UnicodeDecodeError) as e:
            logging.error(f"Failed to read input file '{args.input}': {e}")
            sys.exit(1)
    elif args.text:
        german_input = args.text
        logging.info("Read input from --text argument.")
        input_source = "arg"
    else:
        # Read from stdin if no input argument provided
        if sys.stdin.isatty():
            print("Enter German text (press Ctrl+D or Ctrl+Z to finish):", file=sys.stderr)
        try:
            german_input = sys.stdin.read().strip()
            if not german_input:
                logging.error("No input provided")
                sys.exit(1)
            input_source = "stdin"
        except KeyboardInterrupt:
            sys.exit(1)

    # Translation
    english_translation = translate_text(german_input)
    if english_translation is None:
        print("Translation failed.", file=sys.stderr)
        sys.exit(1)

    # Output handling
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(english_translation)
            logging.info(f"Wrote translation to output file: {args.output}")
        except (PermissionError, IOError) as e:
            logging.error(f"Failed to write to output file '{args.output}': {e}")
            sys.exit(1)
    else:
        # Format output based on input source
        if input_source in ["file", "arg"]:
            # Maintain original formatted output for explicit inputs
            print("\n--- Translation ---")
            print("German: ", german_input)
            print("English:", english_translation)
            print("-------------------")
        else:
            # For stdin input, print only the translation for clean piping
            print(english_translation)


if __name__ == "__main__":
    main()