# Ollama CLI Tool

A simple command-line tool I built to interact with local Ollama AI models. I got tired of switching between different interfaces, so I made this to keep everything in the terminal where I spend most of my time.

## Features

- **List Models**: See what models you have available (because I always forget what I've pulled)
- **Run Prompts**: Send prompts to any model directly from the command line
- **Flexible Input**: Works with command line args, pipes, or just ask you interactively
- **Auto Model Selection**: Picks the first available model if you don't specify one (lazy but convenient)
- **Verbose Mode**: Shows you the full JSON response when you're debugging
- **Helpful Errors**: Actually tells you what went wrong and how to fix it

## Prerequisites

- Python 3.6 or higher
- [Ollama](https://ollama.ai/) installed and running
- At least one model pulled (e.g., `ollama pull llama3.1`)

## Getting started

1. Download or clone this repo
2. Install the one dependency:
   ```bash
   pip install -r requirements.txt
   ```
   That's it! The requirements file is pretty minimal.

## How to use it

### See what models you have

```bash
python cli.py list
```

This will show all models available on your Ollama server.

### Ask something

#### Command Line Input
```bash
python cli.py run "What is Python?"
```

#### Interactive Input
```bash
python cli.py run
# It'll prompt you for input
```

#### Pipe Input
```bash
echo "Explain machine learning" | python cli.py run
```
This is actually pretty handy when you want to analyze files or other command outputs.

### Advanced Options

#### Specify a Model
```bash
python cli.py run "What is Python?" --model llama3.1
```

#### Use a different server
```bash
python cli.py run "Hello" --base-url http://remote-server:11434
```

#### Give it more time
```bash
python cli.py run "Long prompt" --timeout 600
```

#### Verbose Output
```bash
python cli.py run "What is Python?" --verbose
```
This shows you the full JSON response, which is useful when things aren't working as expected.

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

The goal is to tell you what's wrong and how to fix it, not just throw an error at you.

### Basic Workflow
```bash
# 1. Check what models are available
python cli.py list

# 2. Run a simple prompt
python cli.py run "What is machine learning?"

# 3. Be specific about which model
python cli.py run "Explain Python" --model llama3.1
```

### Advanced Usage
```bash
# Analyze a file
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
   - You need to pull a model first: `ollama pull llama3.1`
   - Or check what you have: `ollama list`

3. **"Model not found"**
   - Check what models you actually have: `python cli.py list`
   - Pull the model you want: `ollama pull model-name`

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

The code is pretty straightforward if you want to poke around or modify it. The main logic is in `cli.py` and it's not too complicated.