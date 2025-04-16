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
        logging.info(f"Loading translation model: {model_name}...")
        # Note: The model will be downloaded automatically on first use
        # and cached locally for subsequent runs.
        translator = pipeline("translation_de_to_en", model=model_name)
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
        logging.error(f"ImportError: {e}. Make sure 'torch' or 'tensorflow' is installed.")
        logging.error("Try running: pip install torch")  # Or tensorflow if preferred
        sys.exit(1)  # Exit if core dependency is missing
    except Exception as e:
        logging.error(f"An error occurred during translation: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="German-to-English translation CLI tool.")
    group = parser.add_mutually_exclusive_group(required=True)
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
        except (FileNotFoundError, PermissionError, IOError, UnicodeDecodeError) as e:
            logging.error(f"Failed to read input file '{args.input}': {e}")
            sys.exit(1)
    else:
        german_input = args.text
        logging.info("Read input from --text argument.")

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
        print("German:")
        print(german_input)
        print("\nEnglish:")
        print(english_translation)


if __name__ == "__main__":
    main()