# Ollama CLI Tool

A command-line interface for interacting with local Ollama AI models. This tool provides a simple way to list available models and run prompts through them.

## Features

- **List Models**: View all available Ollama models on your server
- **Run Prompts**: Execute prompts through any available model
- **Flexible Input**: Accept prompts via command line, stdin, or interactive input
- **Auto Model Selection**: Automatically use the first available model if none specified
- **Verbose Mode**: Option to view full JSON responses for debugging
- **Error Handling**: Comprehensive error messages with helpful suggestions

## Prerequisites

- Python 3.6 or higher
- [Ollama](https://ollama.ai/) installed and running
- At least one model pulled (e.g., `ollama pull llama3.1`)

## Installation

1. Clone or download this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### List Available Models

```bash
python cli.py list
```

This will show all models available on your Ollama server.

### Run a Prompt

#### Command Line Input
```bash
python cli.py run "What is Python?"
```

#### Interactive Input
```bash
python cli.py run
# Then enter your prompt when prompted
```

#### Pipe Input
```bash
echo "Explain machine learning" | python cli.py run
```

### Advanced Options

#### Specify a Model
```bash
python cli.py run "What is Python?" --model llama3.1
```

#### Use Different Server
```bash
python cli.py run "Hello" --base-url http://remote-server:11434
```

#### Set Timeout
```bash
python cli.py run "Long prompt" --timeout 600
```

#### Verbose Output
```bash
python cli.py run "What is Python?" --verbose
```

## Command Reference

### `list` Command
Lists all available models on the Ollama server.

**Options:**
- `--base-url`: Ollama server URL (default: http://localhost:11434)

**Example:**
```bash
python cli.py list --base-url http://localhost:11434
```

### `run` Command
Runs a prompt through a specified model.

**Arguments:**
- `prompt`: The text prompt to send to the model (optional - can be provided via stdin or interactive input)

**Options:**
- `--model`: Model name to use (default: first available model)
- `--base-url`: Ollama server URL (default: http://localhost:11434)
- `--timeout`: Request timeout in seconds (default: 300)
- `--verbose`: Show full JSON response (default: false)

**Examples:**
```bash
# Basic usage
python cli.py run "What is Python?"

# With specific model
python cli.py run "Explain quantum computing" --model llama3.1

# With verbose output
python cli.py run "Hello" --verbose

# With custom timeout
python cli.py run "Long prompt" --timeout 600
```

## Error Handling

The tool provides helpful error messages for common issues:

- **Connection Error**: "Cannot connect to Ollama. Is it running? (Try: ollama serve)"
- **No Models**: "No models found. Try: ollama pull llama3.1"
- **Model Not Found**: "Model 'modelname' not found. Run 'list' or pull the model."
- **Timeout**: "Request timed out after X seconds."

## Examples

### Basic Workflow
```bash
# 1. Check what models are available
python cli.py list

# 2. Run a simple prompt
python cli.py run "What is machine learning?"

# 3. Use a specific model
python cli.py run "Explain Python" --model llama3.1
```

### Advanced Usage
```bash
# Pipe content from a file
cat my_questions.txt | python cli.py run

# Use with different server
python cli.py run "Hello" --base-url http://192.168.1.100:11434

# Debug mode to see full responses
python cli.py run "Test" --verbose
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   - Make sure Ollama is running: `ollama serve`
   - Check if the server URL is correct

2. **"No models found"**
   - Pull a model: `ollama pull llama3.1`
   - Check available models: `ollama list`

3. **"Model not found"**
   - List available models: `python cli.py list`
   - Pull the specific model you need

4. **Request timeouts**
   - Increase timeout: `--timeout 600`
   - Try a simpler prompt
   - Check server performance

### Getting Help

Run any command with `--help` to see detailed usage information:
```bash
python cli.py --help
python cli.py list --help
python cli.py run --help
```

## Development

### Project Structure
```
├── cli.py          # Main CLI application
├── requirements.txt # Python dependencies
└── README.md       # This file
```

### Dependencies
- `requests`: HTTP client for API calls
- `argparse`: Command-line argument parsing

## License

This project is part of the Macmillan assignment.

## Contributing

This is an assignment project. For questions or issues, please refer to the assignment guidelines.
