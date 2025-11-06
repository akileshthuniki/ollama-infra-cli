"""
Ollama API Gateway - Production-grade Flask application serving as gateway to local Ollama.

This application provides:
- HTTP REST API wrapping local Ollama instance
- Health check endpoint for AWS ALB
- Prometheus metrics for monitoring
- Comprehensive logging and error handling
- Security best practices (CORS headers, input validation)
- AWS ECS Fargate compatible deployment

Endpoints:
- GET  /health              : Health check for load balancer
- GET  /metrics             : Prometheus metrics
- POST /api/analyze         : AI analysis endpoint
- GET  /api/models          : List available models
- GET  /                    : API information

Environment Variables:
- OLLAMA_URL               : Ollama server URL (default: http://localhost:11434)
- PORT                     : HTTP port (default: 8080)
- ENVIRONMENT              : Environment name (development/staging/production)
- AWS_REGION               : AWS region for context
- ECS_CLUSTER              : ECS cluster name for context
- CONTAINER_ID             : Container ID/task ARN
- LOG_LEVEL                : Logging level (default: INFO)
"""

import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple

import requests
from flask import Flask, jsonify, request, Response, g
from prometheus_flask_exporter import PrometheusMetrics

# =============================================================================
# Configuration and Setup
# =============================================================================

class Config:
    """Application configuration from environment variables."""
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    PORT = int(os.environ.get('PORT', '8080'))
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    ECS_CLUSTER = os.environ.get('ECS_CLUSTER', 'unknown')
    CONTAINER_ID = os.environ.get('CONTAINER_ID', 'unknown')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # API configuration
    MAX_PROMPT_LENGTH = 10000  # Maximum prompt length to accept
    OLLAMA_TIMEOUT = 300  # Timeout for Ollama requests
    OLLAMA_MAX_RETRIES = 3
    
    # Preferred models in order of preference
    PREFERRED_MODELS = ['llama3.1', 'llama3', 'llama2', 'mistral', 'neural-chat']


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """
    Configure structured logging for production environments.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('ollama-gateway')
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler with structured format
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logger = setup_logging(Config.LOG_LEVEL)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('ollama_gateway_info', 'Ollama Gateway Metadata',
             version='1.0.0',
             environment=Config.ENVIRONMENT,
             aws_region=Config.AWS_REGION)

@app.route('/health')
def health():
    """Health check endpoint for load balancer."""
    logger.info("Health check request received")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': Config.ENVIRONMENT,
        'ollama_url': Config.OLLAMA_URL
    })

# Setup logging
logger = setup_logging(Config.LOG_LEVEL)

logger.info(f"Starting Ollama Gateway - Environment: {Config.ENVIRONMENT}")
logger.debug(f"Ollama URL: {Config.OLLAMA_URL}")
logger.debug(f"AWS Region: {Config.AWS_REGION}")

# Track app startup time for metrics
app_start_time = time.time()


# =============================================================================
# Request Tracking and Logging
# =============================================================================

@app.before_request
def add_request_id():
    """Add unique request ID for tracing."""
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    g.request_id = request_id
    request.id = request_id


@app.after_request
def add_security_headers(response):
    """Add request ID and CORS headers."""
    response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
    
    # CORS headers for demo.html access
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID'
    
    return response


def get_client_ip():
    """Get client IP address, accounting for ALB proxy."""
    return request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()


# =============================================================================
# Ollama Integration
# =============================================================================

def _get_ollama_models() -> list:
    """
    Fetch available models from Ollama with retry logic.
    
    Returns:
        List of model names or empty list on error
    """
    for attempt in range(Config.OLLAMA_MAX_RETRIES):
        try:
            response = requests.get(
                f"{Config.OLLAMA_URL}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m.get('name') for m in models if m.get('name')]
        except requests.RequestException as e:
            logger.debug(f"Ollama connection attempt {attempt + 1} failed: {e}")
            if attempt == Config.OLLAMA_MAX_RETRIES - 1:
                logger.error(f"Failed to connect to Ollama after {Config.OLLAMA_MAX_RETRIES} attempts")
                raise
            time.sleep(0.5 * (2 ** attempt))  


def _select_best_model(models: list) -> str:
    """
    Select the best available model from list of models.
    
    Prioritizes models in PREFERRED_MODELS list, falls back to first available.
    
    Args:
        models: List of available model names
        
    Returns:
        Model name to use
        
    Raises:
        ValueError: If no models available
    """
    if not models:
        raise ValueError("No Ollama models available")
    
    # Try preferred models in order
    for preferred in Config.PREFERRED_MODELS:
        for model in models:
            if preferred.lower() in model.lower():
                logger.debug(f"[{g.request_id}] Selected preferred model: {model}")
                return model
    
    # Fallback to first available
    logger.debug(f"[{g.request_id}] No preferred model found, using first available: {models[0]}")
    return models[0]  


def _call_ollama(model: str, prompt: str) -> str:
    """
    Send prompt to Ollama model and return response with retry logic.
    
    Args:
        model: Model name to use
        prompt: The prompt text
        
    Returns:
        Model response text
        
    Raises:
        requests.RequestException: If Ollama call fails after retries
        ValueError: If response is invalid
    """
    for attempt in range(Config.OLLAMA_MAX_RETRIES):
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False
            }
            
            response = requests.post(
                f"{Config.OLLAMA_URL}/api/generate",
                json=payload,
                timeout=Config.OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            if 'response' not in data:
                raise ValueError(f"Invalid Ollama response: {data}")
            
            if attempt > 0:
                logger.info(f"[{g.request_id}] Ollama call succeeded on attempt {attempt + 1}")
            
            return data['response']
            
        except requests.Timeout as e:
            logger.warning(f"[{g.request_id}] Ollama timeout (attempt {attempt + 1}/{Config.OLLAMA_MAX_RETRIES}): {e}")
            if attempt == Config.OLLAMA_MAX_RETRIES - 1:
                raise requests.RequestException(f"Ollama request timed out after {Config.OLLAMA_MAX_RETRIES} attempts")
            time.sleep(0.5 * (2 ** attempt))  # Exponential backoff
            
        except requests.RequestException as e:
            logger.warning(f"[{g.request_id}] Ollama call failed (attempt {attempt + 1}/{Config.OLLAMA_MAX_RETRIES}): {e}")
            if attempt == Config.OLLAMA_MAX_RETRIES - 1:
                raise
            time.sleep(0.5 * (2 ** attempt))  # Exponential backoff


# =============================================================================
# Health and Info Endpoints
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Liveness check endpoint for AWS ALB.
    
    Always returns 200 OK if the container is running.
    This tells the ALB the container is alive, not whether it's ready to serve traffic.
    
    Returns:
        200 OK if container is running
    """
    uptime = time.time() - app_start_time
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime_seconds': round(uptime, 2),
        'environment': Config.ENVIRONMENT,
        'container_id': Config.CONTAINER_ID
    }), 200


@app.route('/health/ready', methods=['GET'])
def readiness_check() -> Tuple[Dict[str, Any], int]:
    """
    Readiness check endpoint for deployment validation.
    
    Verifies that:
    1. Container is running (always true)
    2. Can connect to Ollama service
    3. At least one model is available
    
    Use /health/ready to determine if the container should receive traffic.
    Use /health for basic liveness checking by ALB.
    
    Returns:
        200 OK if ready to serve traffic
        503 Service Unavailable if Ollama is down or no models
    """
    try:
        # Quick check: can we connect to Ollama?
        response = requests.get(
            f"{Config.OLLAMA_URL}/api/tags",
            timeout=2
        )
        response.raise_for_status()
        
        models = response.json().get('models', [])
        if not models:
            logger.warning(f"[{g.request_id}] No Ollama models available")
            return jsonify({
                'status': 'not_ready',
                'reason': 'No models available',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 503
        
        return jsonify({
            'status': 'ready',
            'models_available': len(models),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except requests.RequestException as e:
        logger.warning(f"[{g.request_id}] Readiness check failed: {e}")
        return jsonify({
            'status': 'not_ready',
            'reason': 'Ollama service unavailable',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 503


@app.route('/', methods=['GET'])
def api_info() -> Tuple[Dict[str, Any], int]:
    """
    API information and status endpoint.
    
    Provides metadata about the service and available endpoints.
    """
    return jsonify({
        'service': 'Ollama API Gateway',
        'version': '1.0.0',
        'environment': Config.ENVIRONMENT,
        'aws_region': Config.AWS_REGION,
        'ecs_cluster': Config.ECS_CLUSTER,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'endpoints': {
            'GET /health': 'Liveness check for ALB (always 200)',
            'GET /health/ready': 'Readiness check (503 if Ollama down)',
            'GET /': 'This endpoint',
            'GET /metrics': 'Prometheus metrics',
            'GET /api/models': 'List available models',
            'POST /api/analyze': 'AI analysis endpoint'
        },
        'documentation': 'https://github.com/yourusername/ollama-infra-cli'
    }), 200


@app.route('/api/models', methods=['GET'])
@metrics.counter('ollama_models_list', 'Models list endpoint calls')
def list_models() -> Tuple[Dict[str, Any], int]:
    """
    Get list of available Ollama models.
    
    Returns:
        JSON list of model names
    """
    try:
        models = _get_ollama_models()
        logger.debug(f"Listed {len(models)} available models")
        return jsonify({
            'models': models,
            'count': len(models),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
    except requests.RequestException as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({
            'error': 'Failed to connect to Ollama service',
            'details': str(e)
        }), 503


# =============================================================================
# Analysis Endpoint
# =============================================================================

@app.route('/api/analyze', methods=['OPTIONS'])
def analyze_options():
    """Handle CORS preflight requests for /api/analyze."""
    return '', 200


@app.route('/api/analyze', methods=['POST'])
@metrics.counter('ollama_analyze_requests', 'Analysis endpoint calls')
@metrics.histogram(
    'ollama_analyze_duration_seconds',
    'Analysis request duration',
    labels={'context': lambda: request.json.get('context', 'unknown')}
)
def analyze() -> Tuple[Dict[str, Any], int]:
    """
    Main AI analysis endpoint.
    
    Accepts a prompt and optional model/context, sends to Ollama for analysis.
    
    Request JSON:
    {
        "prompt": "What is Kubernetes?",           # Required: Analysis prompt
        "model": "llama2",                         # Optional: Specific model to use
        "context": "aws|kubernetes|docker",        # Optional: Analysis context
        "max_tokens": 1000                         # Optional: Response length hint
    }
    
    Response JSON:
    {
        "response": "Kubernetes is...",
        "model": "llama2",
        "context": "kubernetes",
        "processing_time_ms": 1234,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    Returns:
        JSON response with AI analysis
    """
    try:
        client_ip = get_client_ip()
        logger.info(f"[{g.request_id}] Analysis request from {client_ip}")
        
        # Validate request format
        if not request.is_json:
            logger.warning(f"[{g.request_id}] Invalid content-type for /analyze endpoint")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'prompt' not in data:
            logger.warning(f"[{g.request_id}] Missing prompt field in analyze request")
            return jsonify({'error': 'Field "prompt" is required'}), 400
        
        prompt = str(data['prompt']).strip()
        
        # Validate prompt
        if not prompt:
            logger.warning(f"[{g.request_id}] Empty prompt provided")
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        if len(prompt) > Config.MAX_PROMPT_LENGTH:
            logger.warning(f"[{g.request_id}] Prompt exceeds max length: {len(prompt)} > {Config.MAX_PROMPT_LENGTH}")
            return jsonify({
                'error': f'Prompt exceeds maximum length of {Config.MAX_PROMPT_LENGTH} characters'
            }), 413
        
        # Get model to use
        model = data.get('model')
        if not model:
            try:
                models = _get_ollama_models()
                model = _select_best_model(models)
                logger.debug(f"[{g.request_id}] Auto-selected model: {model}")
            except (requests.RequestException, ValueError) as e:
                logger.error(f"[{g.request_id}] Failed to get models: {e}")
                return jsonify({'error': 'Cannot connect to Ollama service or no models available'}), 503
        
        # Extract optional fields
        context = data.get('context', 'general').lower()
        
        # Log request details
        logger.info(f"[{g.request_id}] Analysis request: model={model}, context={context}, prompt_length={len(prompt)}")
        
        # Call Ollama
        start_time = time.time()
        try:
            response = _call_ollama(model, prompt)
            processing_time_ms = round((time.time() - start_time) * 1000, 2)
            
            logger.info(f"[{g.request_id}] Analysis completed successfully in {processing_time_ms}ms")
            
            return jsonify({
                'response': response,
                'model': model,
                'context': context,
                'processing_time_ms': processing_time_ms,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
            
        except requests.Timeout:
            logger.error(f"[{g.request_id}] Ollama request timed out after {Config.OLLAMA_TIMEOUT}s")
            return jsonify({
                'error': 'Analysis timed out',
                'details': f'Request exceeded {Config.OLLAMA_TIMEOUT}s timeout'
            }), 504
        except requests.RequestException as e:
            logger.error(f"[{g.request_id}] Ollama request failed: {e}")
            return jsonify({
                'error': 'Failed to connect to Ollama service',
                'details': str(e)
            }), 503
        except ValueError as e:
            logger.error(f"Invalid Ollama response: {e}")
            return jsonify({
                'error': 'Invalid response from Ollama',
                'details': str(e)
            }), 502
    
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': 'An unexpected error occurred'
        }), 500


# =============================================================================
# Error Handlers
# =============================================================================

@app.errorhandler(404)
def not_found(error: Any) -> Tuple[Dict[str, Any], int]:
    """Handle 404 errors."""
    logger.warning(f"[{g.request_id}] 404 Not Found: {request.path}")
    return jsonify({
        'error': 'Endpoint not found',
        'path': request.path,
        'method': request.method
    }), 404


@app.errorhandler(405)
def method_not_allowed(error: Any) -> Tuple[Dict[str, Any], int]:
    """Handle 405 errors."""
    logger.warning(f"[{g.request_id}] 405 Method Not Allowed: {request.method} {request.path}")
    return jsonify({
        'error': 'Method not allowed',
        'method': request.method,
        'path': request.path
    }), 405


@app.errorhandler(500)
def internal_error(error: Any) -> Tuple[Dict[str, Any], int]:
    """Handle 500 errors."""
    logger.error(f"[{g.request_id}] Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'request_id': g.request_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 500


# =============================================================================
# Request Logging and Security
# =============================================================================

@app.after_request
def add_security_headers(response: Response) -> Response:
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Only add HSTS if using HTTPS (check X-Forwarded-Proto for ALB)
    is_secure = request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https'
    if is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info(f"Starting Ollama Gateway on 0.0.0.0:{Config.PORT}")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    
    # Use gunicorn in production, Flask development server otherwise
    if Config.ENVIRONMENT == 'production':
        logger.info("Running in production mode - use gunicorn with multiple workers")
    
    # Disable debug mode to prevent reloader issues in testing
    # Set FLASK_ENV=development if you need debug mode
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=False,
        use_reloader=False
    )

