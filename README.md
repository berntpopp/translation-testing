# German-English Translator CLI

A command-line interface tool that translates German text to English using the Hugging Face transformers library. By default, it uses the Helsinki-NLP/opus-mt-de-en model but supports other translation models as well.

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

The CLI tool supports flexible input, output, and model configuration options:

### Input Options
- `--text "GERMAN_TEXT"` : Provide German text directly as a command-line argument
- `-i INPUT_FILE`, `--input INPUT_FILE` : Specify a file containing German text to translate
- If no input option is provided, the tool reads from standard input (stdin)

### Output Options
- `-o OUTPUT_FILE`, `--output OUTPUT_FILE` : Write only the translated English text to the specified file
- If omitted, output behavior depends on the input source:
  - For stdin input: Only the translation is printed to stdout (suitable for piping)
  - For --text or --input: Formatted output with labels is printed to stdout

### Model Configuration
- `-m MODEL_NAME`, `--model MODEL_NAME` : Specify a Hugging Face model name (default: "Helsinki-NLP/opus-mt-de-en")
- `-l LENGTH`, `--max-length LENGTH` : Set maximum sequence length for translation (default: 512)

### Examples

#### Basic Usage
```bash
# macOS/Linux
# Translate direct text using default model
python3 -m german_translator_cli.translate_cli --text "Guten Morgen!"

# Use a different translation model
python3 -m german_translator_cli.translate_cli --text "Guten Morgen!" --model "facebook/wmt19-de-en"

# Translate longer text with increased max length
python3 -m german_translator_cli.translate_cli --text "Ein sehr langer deutscher Text..." --max-length 1024

# Combine model selection with file input/output
python3 -m german_translator_cli.translate_cli --input german.txt --output english.txt --model "facebook/wmt19-de-en"

# Windows
python -m german_translator_cli.translate_cli --text "Guten Morgen!" --model "facebook/wmt19-de-en"
```

#### Using Pipes and Standard Input/Output
```bash
# macOS/Linux
# Pipe text directly to the translator
echo "Guten Tag" | python3 -m german_translator_cli.translate_cli

# Translate a file using cat and pipes
cat german.txt | python3 -m german_translator_cli.translate_cli

# Pipe text through multiple commands
echo "Guten Tag" | python3 -m german_translator_cli.translate_cli | grep "Hello"

# Save translation to a file using shell redirection
echo "Guten Tag" | python3 -m german_translator_cli.translate_cli > english.txt

# Process multiple translations from a file, one per line
cat german_phrases.txt | while read line; do
    echo "$line" | python3 -m german_translator_cli.translate_cli
done

# Windows
echo "Guten Tag" | python -m german_translator_cli.translate_cli
```

### Interactive Mode
When no input source is specified and the input is from a terminal, the tool enters interactive mode:
```bash
# macOS/Linux
python3 -m german_translator_cli.translate_cli
# Windows
python -m german_translator_cli.translate_cli

Enter German text (press Ctrl+D or Ctrl+Z to finish):
Guten Tag, wie geht es Ihnen?
[Press Ctrl+D (Unix) or Ctrl+Z (Windows)]
```

### Notes
- You must provide exactly one of `--text` or `--input`.
- If `--output` is not specified, the tool prints both the original German and the English translation to stdout.
- If `--output` is specified, only the English translation is written to the file.
- Errors in file reading/writing are logged and cause the program to exit with status 1.

For sentences with spaces, make sure to enclose the text in quotes as shown above.

### Example Output

```
2025-04-15 12:34:56 - INFO - Input German text: 'Der Patient hat starke Kopfschmerzen und Fieber.'
2025-04-15 12:34:56 - INFO - Loading translation model: Helsinki-NLP/opus-mt-de-en...
2025-04-15 12:34:58 - INFO - Model loaded. Starting translation...
2025-04-15 12:35:00 - INFO - Translation successful.

--- Translation ---
German:  Der Patient hat starke Kopfschmerzen und Fieber.
English: The patient has severe headaches and fever.
-------------------
```

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