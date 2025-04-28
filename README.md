# Universal Text Translator CLI

A command-line interface tool that translates text between any supported language pair using the Helsinki-NLP models from Hugging Face. By default, it translates from German (de) to English (en), but supports any language pair available in the Helsinki-NLP collection.

## Prerequisites

### Windows
- Python 3.7 or higher
- pip (Python package installer)

### macOS
- Python 3.7 or higher (use python3)
- pip3 (Python package installer)
  ```bash
  # Check if python3 is installed
  python3 --version
  
  # If needed, install Python3 via Homebrew
  brew install python3
  ```

### Linux
- Python 3.7 or higher
- pip (Python package installer)
- Required system packages:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-venv python3-pip
  ```
  For other Linux distributions, use the appropriate package manager (yum, dnf, pacman, etc.)

## Project Structure
```
.
├── LICENSE
├── README.md
├── requirements.txt
└── german_translator_cli/
    └── translate_cli.py
```

## Installation

1. Clone this repository or download the source code:
   ```bash
   git clone <repository-url>
   cd translation-testing
   ```

2. Create and activate a virtual environment:

   ### macOS
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify activation (should show virtual environment path)
   which python3
   ```

   ### Linux
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify activation (should show virtual environment path)
   which python
   ```

   ### Windows
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   
   ### macOS/Linux
   ```bash
   pip3 install -r requirements.txt
   ```

   Optional: For better download performance of the model, you can install the additional package:
   ```bash
   pip3 install huggingface_hub[hf_xet]
   ```
   or
   ```bash
   pip3 install hf_xet
   ```

   ### Windows
   ```bash
   pip install -r requirements.txt
   ```

   Optional: For better download performance of the model, you can install the additional package:
   ```bash
   pip install huggingface_hub[hf_xet]
   ```
   or
   ```bash
   pip install hf_xet
   ```

4. (Linux only) Make the script executable:
   ```bash
   chmod +x german_translator_cli/translate_cli.py
   ```

## Usage

The CLI tool supports flexible input, output, and language configuration options:

### Language Options
- `-s LANG_CODE`, `--source-lang LANG_CODE`: Source language code (default: de)
- `-t LANG_CODE`, `--target-lang LANG_CODE`: Target language code (default: en)
- `-m MODEL_NAME`, `--model MODEL_NAME`: Optional specific model name to use (overrides language pair settings)

### Input Options
- `--text "TEXT"`: Provide source text directly as a command-line argument
- `-i INPUT_FILE`, `--input INPUT_FILE`: Specify a file containing text to translate
- If no input option is provided, the tool reads from standard input (stdin)

### Output Options
- `-o OUTPUT_FILE`, `--output OUTPUT_FILE`: Write only the translated text to the specified file
- If omitted, output behavior depends on the input source:
  - For stdin input: Only the translation is printed to stdout (suitable for piping)
  - For --text or --input: Formatted output with labels is printed to stdout

### Model Configuration
- `-l LENGTH`, `--max-length LENGTH`: Set maximum sequence length for translation (default: 512)

### Logging Options
- `--log-level LEVEL`: Sets the verbosity of the logging output. Available levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL (default: INFO)
- `--log-format FORMAT`: Specifies the format string for log messages using Python's standard logging format syntax (default: "%(asctime)s - %(levelname)s - %(message)s")

### Examples

#### Basic Usage with Different Language Pairs
```bash
# Translate from Spanish to English
python3 -m german_translator_cli.translate_cli --text "¡Buenos días!" -s es -t en

# Translate from English to French
python3 -m german_translator_cli.translate_cli --text "Hello, world!" -s en -t fr

# Use specific model (overrides language pair settings)
python3 -m german_translator_cli.translate_cli --text "Hello" --model "Helsinki-NLP/opus-mt-en-fr"

# Translate file from German to Spanish
python3 -m german_translator_cli.translate_cli -i input.txt -o output.txt -s de -t es
```

#### Using Pipes with Different Languages
```bash
# Pipe Spanish text to English translation
echo "¡Hola mundo!" | python3 -m german_translator_cli.translate_cli -s es -t en

# Chain translations (Spanish -> English -> French)
echo "¡Hola mundo!" | \
  python3 -m german_translator_cli.translate_cli -s es -t en | \
  python3 -m german_translator_cli.translate_cli -s en -t fr
```

#### Using Different Logging Levels
```bash
# Run with debug-level logging
python3 -m german_translator_cli.translate_cli --text "Hallo Welt" --log-level DEBUG

# Run with minimal (error-only) logging
python3 -m german_translator_cli.translate_cli -i input.txt -o output.txt --log-level ERROR

# Use custom log format (showing only level and message)
python3 -m german_translator_cli.translate_cli --text "Guten Tag" --log-format "%(levelname)s: %(message)s"
```

### Language Codes

Common language codes for reference:
- de: German
- en: English
- es: Spanish
- fr: French
- it: Italian
- pt: Portuguese
- ru: Russian
- zh: Chinese

For a complete list of supported language pairs, visit:
https://huggingface.co/Helsinki-NLP

### Error Handling

The tool includes comprehensive error handling for language pairs:
- Verifies if the requested language pair model exists
- Provides clear error messages if a language pair is not supported
- Suggests checking the Helsinki-NLP page for available models

## First Run Notice

On the first run, the tool will download the Helsinki-NLP/opus-mt-de-en model (approximately 300MB). This model will be cached locally for subsequent uses, making future translations much faster.

The model is cached in:
- Windows: `%USERPROFILE%\.cache\huggingface\hub`
- Linux/macOS: `~/.cache/huggingface/hub`

### Linux Permissions
If you encounter permission issues with the cache directory on Linux:
```bash
# Create the cache directory with correct permissions
mkdir -p ~/.cache/huggingface/hub
chmod 755 ~/.cache/huggingface
```

## Memory Requirements

- Minimum RAM: 4GB
- Recommended RAM: 8GB or more
- Disk Space: At least 1GB free space (for model cache and virtual environment)

### Linux Memory Management
If you encounter memory issues on Linux, you can check available memory:
```bash
free -h
```

If needed, you can create/adjust swap space:
```bash
# Check current swap
swapon --show

# Create a swap file (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Error Handling

The tool includes comprehensive error handling and will:
- Display informative error messages if dependencies are missing
- Show progress during model loading and translation
- Exit with a non-zero status code if translation fails

### Linux-specific Troubleshooting
If you encounter CUDA/GPU-related errors on Linux:
1. Check NVIDIA driver installation:
   ```bash
   nvidia-smi
   ```
2. Verify PyTorch installation with CUDA support:
   ```bash
   python3 -c "import torch; print(torch.cuda.is_available())"
   ```

## Troubleshooting

### Common Messages

1. Xet Storage Warning:
   If you see this message:
   ```
   Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. 
   Falling back to regular HTTP download.
   ```
   This is not an error - it simply means the tool is using standard HTTP download for the model. 
   The translation will work normally, just slightly slower during the initial model download. 
   To improve download speed, follow the installation instructions for the optional `hf_xet` package above.

## Deactivating the Virtual Environment

When you're done using the translator:
```bash
deactivate
```

## License

This project is licensed under the MIT License, see the LICENSE file for details.