"""
Ollama CLI - Simple local AI wrapper for analyzing any text data.

Pipes any command output through Ollama for AI analysis without sending data to external services.

Features:
- List available local Ollama models
- Run prompts with any Ollama model
- Accept input from command line, stdin, or pipes
- Simple configuration via environment variables
- Works with any infrastructure/log data

Usage Examples:
    # List models
    python cli.py list
    
    # Run a prompt directly
    python cli.py run "Explain this code"
    
    # Pipe data for analysis
    echo "error logs here" | python cli.py run "summarize these errors"
    kubectl logs pod-name | python cli.py run "why is this failing?"
    aws ec2 describe-instances | python cli.py run "analyze my instances"
    
    # Run interactively
    python cli.py run

Prerequisites:
    - Python 3.8+
    - Ollama running locally (http://localhost:11434)
    - At least one model pulled: ollama pull llama2
"""

import argparse
import json
import logging
import os
import sys
from typing import List, Optional

import requests

# =============================================================================
# Configuration
# =============================================================================

OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL')
TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '300'))  # 5 minutes for AI responses
DEBUG = os.environ.get('DEBUG', '').lower() == 'true'


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure logging."""
    level = logging.DEBUG if debug else logging.INFO
    
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('ollama-cli')
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger


# =============================================================================
# Ollama Integration
# =============================================================================

def list_models(logger: logging.Logger) -> List[str]:
    """Fetch available Ollama models from server."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=TIMEOUT)
        response.raise_for_status()
        
        models = response.json().get("models", [])
        return [m.get("name") for m in models if m.get("name")]
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_URL}")
        logger.error("Is it running? Try: ollama serve")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching models: {e}")
        return []


def run_prompt(prompt: str, model: str, logger: logging.Logger) -> str:
    """Send prompt to Ollama model and get response."""
    try:
        payload = {"model": model, "prompt": prompt, "stream": False}
        
        logger.debug(f"Sending prompt to {model}...")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        data = response.json()
        if "response" not in data:
            raise ValueError(f"Unexpected response: {data}")
        
        return data["response"]
        
    except requests.exceptions.ConnectionError:
        raise requests.RequestException(f"Cannot connect to Ollama at {OLLAMA_URL}")
    except requests.exceptions.Timeout:
        raise requests.RequestException(
            f"Ollama request timed out after {TIMEOUT}s. "
            "AI model is taking too long to respond. Try a simpler prompt or check Ollama logs."
        )
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(f"Ollama error: {e}")



# =============================================================================
# CLI Command Handlers
# =============================================================================

def cmd_list(logger: logging.Logger) -> None:
    """Handle 'list' command - show available Ollama models."""
    try:
        models = list_models(logger)
        
        if not models:
            print("No models found. Pull one with: ollama pull llama2")
            return
        
        print("Available Ollama models:")
        for model in models:
            print(f"  • {model}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_run(args: argparse.Namespace, logger: logging.Logger) -> None:
    """Handle 'run' command - execute a prompt."""
    try:
        # Get prompt from different sources
        prompt = args.prompt
        
        # Try to read from stdin if no prompt provided
        if not prompt and not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        
        # Ask interactively if still no prompt
        if not prompt:
            try:
                prompt = input("Enter your prompt: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled.")
                return
        
        if not prompt:
            logger.error("Prompt is required")
            sys.exit(1)
        
        # Determine model to use
        model = args.model or DEFAULT_MODEL
        if not model:
            models = list_models(logger)
            if not models:
                logger.error("No Ollama models available")
                logger.error("Pull a model with: ollama pull llama2")
                sys.exit(1)
            model = models[0]
            print(f"Using model: {model}", file=sys.stderr)
        
        # Run the prompt
        response = run_prompt(prompt, model=model, logger=logger)
        print(response)
        
    except requests.RequestException as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Ollama CLI - Pipe any data through local AI for analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available models
  python cli.py list
  
  # Run a direct prompt
  python cli.py run "Explain this concept"
  
  # Pipe data through CLI
  echo "error logs" | python cli.py run "summarize these errors"
  kubectl logs pod | python cli.py run "why is this failing?"
  aws ec2 describe-instances | python cli.py run "analyze my instances"
  
  # Set model explicitly
  python cli.py run "analyze this" --model llama2

Environment Variables:
  OLLAMA_URL       Ollama server URL (default: http://localhost:11434)
  OLLAMA_MODEL     Default model to use
  OLLAMA_TIMEOUT   Request timeout in seconds (default: 60)
  DEBUG            Enable debug logging (true/false)
"""
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # List command
    subparsers.add_parser('list', help='List available Ollama models')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a prompt')
    run_parser.add_argument('prompt', nargs='?', help='Prompt text (optional, can be piped)')
    run_parser.add_argument('--model', help='Specific model to use')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(debug=args.debug or DEBUG)
    logger.debug(f"Ollama URL: {OLLAMA_URL}")
    logger.debug(f"Timeout: {TIMEOUT}s")
    
    # Route to handlers
    try:
        if args.command == 'list':
            cmd_list(logger)
        elif args.command == 'run':
            cmd_run(args, logger)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()