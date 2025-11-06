# Ollama API Service

Private AI inference service built with Flask and Ollama. Provides secure AI analysis for DevOps tools.

## 🤖 Overview

### What It Does
- **AI Inference** - Private LLM analysis using Ollama
- **REST API** - HTTP endpoints for AI services
- **DevOps Integration** - Works with DevOps analyzer
- **Secure** - Runs in your private infrastructure

### Architecture
```
src/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── config.py          # Application settings
```

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test the API
curl http://localhost:8080/health
```

### Docker Development
```bash
# Build image
docker build -t ollama-api .

# Run container
docker run -p 8080:8080 ollama-api

# Test API
curl http://localhost:8080/health
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T20:00:00Z",
  "service": "ollama-api"
}
```

### AI Analysis
```bash
POST /api/analyze
Content-Type: application/json

{
  "prompt": "Analyze this infrastructure",
  "context": "devops-analysis"
}
```

**Response:**
```json
{
  "response": "AI analysis result...",
  "model": "llama2",
  "processing_time_ms": 1500
}
```

### Model Information
```bash
GET /api/models
```

**Response:**
```json
{
  "models": ["llama2", "codellama"],
  "current": "llama2"
}
```

## ⚙️ Configuration

### Environment Variables
```bash
# API Configuration
export API_PORT=8080
export API_HOST=0.0.0.0

# Ollama Configuration
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama2

# Security
export API_KEY=your-secret-key
export CORS_ORIGINS=http://localhost:3000
```

### Config File (config.py)
```python
class Config:
    API_PORT = 8080
    OLLAMA_HOST = "http://localhost:11434"
    OLLAMA_MODEL = "llama2"
    TIMEOUT = 30
    MAX_PROMPT_LENGTH = 4000
```

## 🔧 Development

### Adding New Endpoints
```python
@app.route('/api/custom', methods=['POST'])
def custom_endpoint():
    data = request.get_json()
    # Your logic here
    return jsonify({"result": "success"})
```

### Error Handling
```python
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500
```

### Logging
```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use in your code
logger.info("Processing request")
logger.error("Something went wrong")
```

## 🧪 Testing

### Unit Tests
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

### API Testing
```bash
# Health check
curl -f http://localhost:8080/health

# Test AI endpoint
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'

# Test error handling
curl -X POST http://localhost:8080/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

### Load Testing
```bash
# Install Apache Bench
ab -n 100 -c 10 http://localhost:8080/health

# Or use curl in a loop
for i in {1..100}; do
  curl -s http://localhost:8080/health > /dev/null
done
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t ollama-api .
```

### Run Container
```bash
# Basic run
docker run -p 8080:8080 ollama-api

# With environment variables
docker run -p 8080:8080 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  -e API_PORT=8080 \
  ollama-api

# With volume mount
docker run -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  ollama-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  ollama-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
```

## 🔒 Security

### API Key Authentication
```python
@app.before_request
def require_api_key():
    if request.path.startswith('/api/'):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
```

### CORS Configuration
```python
from flask_cors import CORS

CORS(app, origins=[
    "http://localhost:3000",
    "https://your-domain.com"
])
```

### Input Validation
```python
def validate_prompt(prompt):
    if not prompt or len(prompt) > 4000:
        raise ValueError("Invalid prompt")
    return prompt.strip()
```

## 📊 Monitoring

### Health Checks
```bash
# Application health
curl http://localhost:8080/health

# Ollama health
curl http://localhost:11434/api/tags

# Docker health
docker ps
```

### Metrics
```python
# Add metrics endpoint
@app.route('/metrics')
def metrics():
    return jsonify({
        "requests_total": request_count,
        "average_response_time": avg_response_time,
        "error_rate": error_rate
    })
```

### Logging
```python
# Structured logging
import json

@app.before_request
def log_request():
    logger.info(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.path,
        "ip": request.remote_addr
    }))
```

## 🚨 Troubleshooting

### Common Issues

**API not responding?**
```bash
# Check if running
ps aux | grep python

# Check logs
docker logs ollama-api

# Check port
netstat -tlnp | grep 8080
```

**Ollama connection failed?**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check network
telnet localhost 11434

# Check Docker network
docker network ls
```

**High memory usage?**
```bash
# Monitor memory
docker stats ollama-api

# Check model size
curl http://localhost:11434/api/tags

# Restart service
docker restart ollama-api
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
- name: Test API
  run: |
    python app.py &
    sleep 5
    curl -f http://localhost:8080/health
    curl -X POST http://localhost:8080/api/analyze -H "Content-Type: application/json" -d '{"prompt": "test"}'
```

### Docker Registry
```bash
# Build and push
docker build -t your-registry/ollama-api:latest .
docker push your-registry/ollama-api:latest

# Pull and run
docker pull your-registry/ollama-api:latest
docker run -p 8080:8080 your-registry/ollama-api:latest
```

---

**Private AI service ready for DevOps automation!** 🚀
