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
    """
    Parses command-line arguments and initiates the translation process.
    """
    parser = argparse.ArgumentParser(
        description="Translate German text to English using a local NMT model."
    )
    parser.add_argument(
        "text",
        type=str,
        help="The German text to translate (enclose in quotes if it contains spaces)."
    )
    # Optional: Add an argument to specify a different model if needed later
    # parser.add_argument(
    #     "--model",
    #     type=str,
    #     default="Helsinki-NLP/opus-mt-de-en",
    #     help="The Hugging Face model name for German-to-English translation."
    # )

    args = parser.parse_args()

    german_input = args.text
    # model_to_use = args.model  # Use this if the --model argument is added

    logging.info(f"Input German text: '{german_input}'")

    english_translation = translate_text(german_input)  # Pass model_to_use here if added

    if english_translation:
        print("\n--- Translation ---")
        print(f"German:  {german_input}")
        print(f"English: {english_translation}")
        print("-------------------\n")
    else:
        print("\nTranslation failed. Check logs for details.\n", file=sys.stderr)
        sys.exit(1)  # Exit with error status if translation failed


if __name__ == "__main__":
    main()