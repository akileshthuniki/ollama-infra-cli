# Usage Examples

## 🔍 URL Analysis Examples

### Basic URL Check
```bash
python devops-analyzer.py url https://google.com
```

### Performance Analysis
```bash
python devops-analyzer.py url https://slow-website.com --question "Why is this slow?"
```

### Security Audit
```bash
python devops-analyzer.py url https://api.example.com --question "Is this secure?" --output security-report.md
```

### Load Balancer Analysis
```bash
python devops-analyzer.py url https://my-alb.amazonaws.com --question "How can I improve availability?"
```

### Kubernetes Service Check
```bash
python devops-analyzer.py url https://kubernetes.default.svc.cluster.local --question "Are all pods healthy?"
```

## 🏗️ Infrastructure Analysis Examples

### Architecture Documentation
```bash
python devops-analyzer.py infrastructure --type architecture --cluster production --output architecture.md
```

### Health Check for All Services
```bash
python devops-analyzer.py infrastructure --type health --cluster production --output health-report.md
```

### Specific Service Health
```bash
python devops-analyzer.py infrastructure --type health --cluster production --service api-service
```

### Multi-Environment Analysis
```bash
# Production
python devops-analyzer.py infrastructure --type architecture --cluster prod-cluster --output prod-architecture.md

# Staging
python devops-analyzer.py infrastructure --type architecture --cluster staging-cluster --output staging-architecture.md

# Development
python devops-analyzer.py infrastructure --type architecture --cluster dev-cluster --output dev-architecture.md
```

## 🚀 Deployment Analysis Examples

### Pre-Deployment Validation
```bash
python devops-analyzer.py deploy --action pre-check --cluster production --service api-service
```

### Post-Deployment Verification
```bash
python devops-analyzer.py deploy --action post-check --cluster production --service api-service
```

### Full Cluster Deployment Check
```bash
# Before deployment
python devops-analyzer.py deploy --action pre-check --cluster production

# After deployment
python devops-analyzer.py deploy --action post-check --cluster production
```

## 🔄 CI/CD Integration Examples

### GitHub Actions Workflow
```yaml
name: DevOps Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: pip install -r requirements.txt
        
      - name: Pre-deployment check
        run: python devops-analyzer.py deploy --action pre-check --cluster ${{ env.CLUSTER }}
        
      - name: URL health check
        run: python devops-analyzer.py url https://api.${{ env.DOMAIN }} --question "Is everything working?"
```

## 📊 Monitoring Examples

### Daily Health Check Script
```bash
#!/bin/bash
# daily_health_check.sh

DATE=$(date +%Y%m%d)
REPORT_DIR="daily_reports"
mkdir -p $REPORT_DIR

echo "🏥 Running daily health checks..."

# Check production cluster
python devops-analyzer.py infrastructure --type health --cluster production --output "$REPORT_DIR/${DATE}_production_health.md"

# Check staging cluster
python devops-analyzer.py infrastructure --type health --cluster staging --output "$REPORT_DIR/${DATE}_staging_health.md"

# Check critical URLs
URLS=("https://api.example.com" "https://admin.example.com" "https://cdn.example.com")
for url in "${URLS[@]}"; do
    python devops-analyzer.py url $url --output "$REPORT_DIR/${DATE}_$(echo $url | sed 's/https\///g' | sed 's/\./_/g').md"
done

echo "✅ Daily health checks completed. Reports saved to $REPORT_DIR/"
```

### Weekly Architecture Documentation
```bash
#!/bin/bash
# weekly_architecture_docs.sh

DATE=$(date +%Y%m%d)
DOC_DIR="architecture_docs"
mkdir -p $DOC_DIR

echo "📚 Generating weekly architecture documentation..."

CLUSTERS=("production" "staging" "development")
for cluster in "${CLUSTERS[@]}"; do
    python devops-analyzer.py infrastructure --type architecture --cluster $cluster --output "$DOC_DIR/${DATE}_${cluster}_architecture.md"
done

echo "✅ Architecture documentation generated. Files saved to $DOC_DIR/"
```

## 🎯 Real-World Scenarios

### Scenario 1: Production Issue Investigation
```bash
# Step 1: Check the problematic URL
python devops-analyzer.py url https://api.production.com --question "Why are we getting 500 errors?"

# Step 2: Check infrastructure health
python devops-analyzer.py infrastructure --type health --cluster production

# Step 3: Generate incident report
python devops-analyzer.py url https://api.production.com --question "What is the root cause and how to fix it?" --output incident_report.md
```

### Scenario 2: Pre-Deployment Validation
```bash
# Step 1: Check current infrastructure state
python devops-analyzer.py deploy --action pre-check --cluster production

# Step 2: If issues found, generate report
python devops-analyzer.py infrastructure --type health --cluster production --output pre_deployment_health.md

# Step 3: After deployment, verify success
python devops-analyzer.py deploy --action post-check --cluster production --output post_deployment_verification.md
```

### Scenario 3: Performance Optimization
```bash
# Step 1: Analyze slow endpoints
python devops-analyzer.py url https://api.example.com/slow-endpoint --question "Why is this endpoint slow?"

# Step 2: Check infrastructure resources
python devops-analyzer.py infrastructure --type architecture --cluster production --service api-service

# Step 3: Generate optimization recommendations
python devops-analyzer.py url https://api.example.com --question "How can I improve performance across all endpoints?" --output performance_optimization.md
```

### Scenario 4: Security Audit
```bash
# Step 1: Check SSL certificates for all endpoints
ENDPOINTS=("https://api.example.com" "https://admin.example.com" "https://cdn.example.com")
for endpoint in "${ENDPOINTS[@]}"; do
    python devops-analyzer.py url $endpoint --question "Is this secure?" --output "security_audit_$(echo $endpoint | sed 's/https\///g').md"
done

# Step 2: Check infrastructure security
python devops-analyzer.py infrastructure --type architecture --cluster production --output infrastructure_security.md
```

## 🔧 Advanced Usage

### Custom API Endpoint
```bash
# Use your own Ollama API
python devops-analyzer.py url https://example.com --api-url http://my-ollama-api.example.com
```

### Batch Analysis with Custom Questions
```bash
#!/bin/bash
# batch_analysis.sh

URLS=("https://api1.example.com" "https://api2.example.com" "https://api3.example.com")
QUESTIONS=("Is this secure?" "How can I improve performance?" "Are there any issues?")

for url in "${URLS[@]}"; do
    for question in "${QUESTIONS[@]}"; do
        filename="analysis_$(echo $url | sed 's/https\///g' | sed 's/\./_/g')_$(echo $question | sed 's/ /_/g').md"
        python devops-analyzer.py url $url --question "$question" --output "batch_reports/$filename"
    done
done
```

### Integration with Monitoring Tools
```bash
# Integrate with Prometheus/Alertmanager
#!/bin/bash
# alert_integration.sh

ALERT_URL=$1
python devops-analyzer.py url $ALERT_URL --question "What is causing this alert?" --output "alerts/$(date +%Y%m%d_%H%M%S)_alert_analysis.md"

# Send analysis to Slack/Teams
# Add your notification logic here
```

---

**These examples cover most common use cases. Modify them to fit your specific needs!** 🚀
