"""
Ollama CLI Tool - A command-line interface for interacting with local Ollama AI models.

This tool provides two main commands:
- list: Show available models on the Ollama server
- run: Execute a prompt through a specified model

Usage examples:
    python cli.py list
    python cli.py run "What is Python?"
    echo "Explain Kubernetes" | python cli.py run
"""

import argparse
import sys
import requests

def list_models(base_url: str = "http://localhost:11434"):
    """
    List all available Ollama models on the server.
    
    Args:
        base_url: The base URL of the Ollama server (default: http://localhost:11434)
    
    Makes a GET request to the /api/tags endpoint to retrieve model information.
    """
    try:
        # Request model list from Ollama API
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        
        # Extract models from JSON response
        models = response.json().get("models", [])
        
        if not models:
            print("No models found. Try: ollama pull llama3.1")
        else:
            print("Available models:")
            # Print each model name
            for model in models:
                name = model.get("name")
                if name:
                    print(f" - {name}")
                    
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? (Try: ollama serve)")
    except requests.exceptions.Timeout:
        print("Error: Connection timed out.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def get_available_models(base_url: str) -> list:
    """
    Get a list of available model names from the Ollama server.
    
    Args:
        base_url: The base URL of the Ollama server
        
    Returns:
        List of model names, or empty list if request fails
    """
    try:
        # Request model list from Ollama API
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        
        # Extract and filter model names
        models = response.json().get("models", [])
        return [m.get("name") for m in models if m.get("name")]
        
    except requests.exceptions.RequestException:
        # Return empty list if we can't connect or get models
        return []

def run_model(prompt: str, model: str, base_url: str = "http://localhost:11434", timeout_seconds: int = 300, verbose: bool = False):
    """
    Run a prompt through the specified Ollama model and display the response.
    
    Args:
        prompt: The text prompt to send to the model
        model: The name of the model to use
        base_url: The base URL of the Ollama server (default: http://localhost:11434)
        timeout_seconds: Request timeout in seconds (default: 300)
        verbose: If True, show full JSON response along with AI response
    """
    try:
        # Send POST request to Ollama's generate endpoint
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()

        # Show full response if verbose mode is enabled
        if verbose:
            print("=== Full Response ===")
            print(data)
            print("=== AI Response ===")

        # Extract and display the AI's response
        if isinstance(data, dict) and "response" in data:
            print(data["response"])
        else:
            print("Error: Unexpected response format")
            print(data)

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Is it running? (Try: ollama serve)")
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {timeout_seconds} seconds.")
    except requests.exceptions.HTTPError as http_err:
        # Handle specific HTTP errors
        if response.status_code == 404:
            print(f"Error: Model '{model}' not found. Run 'list' or pull the model.")
        else:
            print(f"HTTP Error {response.status_code}: {http_err}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    """
    Main entry point for the CLI application.
    
    Sets up argument parsing for 'list' and 'run' subcommands and handles
    the execution flow based on user input.
    """
    # Configure argument parser with help text and examples
    parser = argparse.ArgumentParser(
        description="Ollama CLI Tool - Interact with local AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollama_cli.py list
  ollama_cli.py run "What is Python?"
  echo "Explain Kubernetes" | ollama_cli.py run
"""
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Configure 'list' subcommand
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama server URL")

    # Configure 'run' subcommand
    run_parser = subparsers.add_parser("run", help="Run a prompt through a model")
    run_parser.add_argument("prompt", type=str, nargs="?", help="Prompt text")
    run_parser.add_argument("--model", default=None, help="Model name to use")
    run_parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama server URL")
    run_parser.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds")
    run_parser.add_argument("--verbose", action="store_true", help="Show full JSON response")

    # Parse command line arguments
    args = parser.parse_args()

    # Handle 'list' command
    if args.command == "list":
        list_models(base_url=args.base_url)

    # Handle 'run' command
    elif args.command == "run":
        # Get prompt from command line argument, stdin, or interactive input
        prompt = args.prompt
        if not prompt:
            if not sys.stdin.isatty():
                # Read from stdin if input is piped
                prompt = sys.stdin.read().strip()
            else:
                # Ask user interactively
                try:
                    prompt = input("Enter prompt: ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\nCancelled.")
                    return

        # Validate that we have a prompt
        if not prompt:
            print("Error: Prompt is required.")
            return

        # Determine which model to use
        model = args.model
        if not model:
            # Auto-select first available model if none specified
            models = get_available_models(args.base_url)
            if not models:
                print("Error: No models available. Use 'list' or pull a model.")
                return
            model = models[0]
            print(f"Using model: {model}")

        # Execute the model with the prompt
        run_model(
            prompt,
            model=model,
            base_url=args.base_url,
            timeout_seconds=args.timeout,
            verbose=args.verbose,
        )

if __name__ == "__main__":
    main()