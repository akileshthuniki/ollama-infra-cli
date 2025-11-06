# DevOps Infrastructure Suite

A complete DevOps toolkit with infrastructure automation, private AI services, and analysis tools.

## 🚀 Quick Start

### Option 1: Deploy Everything
```bash
# Deploy infrastructure
./scripts/deploy.sh staging

# Deploy with DevOps analyzer
./scripts/deploy.sh staging --with-analyzer
```

### Option 2: Use DevOps Analyzer Only
```bash
cd devops-analyzer
pip install -r requirements.txt
python devops-analyzer.py url https://google.com
```

## 📁 Project Structure

```
├── 📄 README.md              # This file - main guide
├── 🚀 scripts/               # Deployment and utility scripts
│   └── deploy.sh            # Main deployment script
├── 🏗️ infra/                 # Infrastructure as Code
│   ├── environments/        # AWS environments (staging, production)
│   └── modules/             # Reusable Terraform modules
├── 🤖 src/                   # Application source code
│   └── app.py               # Main Flask application
├── 🔍 devops-analyzer/       # CLI analysis tools
│   ├── devops-analyzer.py  # Main analyzer tool
│   └── README.md           # Analyzer documentation
├── 🐳 docker/                # Docker configurations
└── ⚙️ config/                # Configuration files
```

## 🎯 What's Included

### 🏗️ **Infrastructure**
- **AWS ECS** - Container orchestration
- **Application Load Balancer** - Traffic distribution
- **VPC Networking** - Secure network setup
- **IAM Roles** - Security and permissions

### 🤖 **Private AI Service**
- **Ollama API** - Private AI inference
- **Flask Backend** - REST API interface
- **Docker Containers** - Containerized deployment

### 🔍 **DevOps Analyzer**
- **URL Analysis** - Check websites and services
- **Infrastructure Analysis** - AWS health and documentation
- **Deployment Checks** - Pre/post deployment validation
- **AI-Powered Insights** - Smart troubleshooting

### 🚀 **Deployment Tools**
- **Automated Scripts** - One-command deployment
- **Environment Management** - Staging/production environments
- **Health Checks** - Post-deployment verification

## 🛠️ Installation

### Prerequisites
- AWS CLI configured
- Docker installed
- Terraform installed
- Python 3.7+ (for analyzer)

### Quick Setup
```bash
# Clone and setup
git clone <repository>
cd <repository>

# Deploy infrastructure
./scripts/deploy.sh staging

# Test deployment
curl https://your-alb-url.amazonaws.com/health
```

## 📖 Usage

### Deploy Infrastructure
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Deploy with analyzer
./scripts/deploy.sh staging --with-analyzer
```

### Use DevOps Analyzer
```bash
cd devops-analyzer

# URL analysis
python devops-analyzer.py url https://your-service.com --question "Why is this slow?"

# Infrastructure analysis
python devops-analyzer.py infrastructure --type architecture --cluster your-cluster

# Deployment checks
python devops-analyzer.py deploy --action pre-check --cluster your-cluster
```

### API Usage
```bash
# Health check
curl https://your-alb-url.amazonaws.com/health

# AI analysis
curl -X POST https://your-alb-url.amazonaws.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this infrastructure"}'
```

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"

# Application Configuration
export OLLAMA_MODEL="llama2"
export API_PORT="8080"
```

### Config Files
- `config/staging.yaml` - Staging environment settings
- `config/production.yaml` - Production environment settings
- `infra/environments/staging/terraform.tfvars` - Terraform variables

## 🚨 Troubleshooting

### Common Issues

**Deployment fails?**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Terraform state
cd infra/environments/staging
terraform plan
```

**Service not responding?**
```bash
# Check logs
aws logs tail /ecs/ollama-api --follow

# Check service health
./scripts/health-check.sh staging
```

**Analyzer not working?**
```bash
# Test without AI
cd devops-analyzer
python devops-analyzer.py url https://google.com --no-ai

# Check API access
curl -I http://your-ollama-api:11434/api/tags
```

## 📊 Monitoring

### Health Checks
```bash
# Infrastructure health
./scripts/health-check.sh staging

# Service health
curl https://your-alb-url.amazonaws.com/health

# Analyzer health
cd devops-analyzer
python devops-analyzer.py infrastructure --type health --cluster staging
```

### Logs
```bash
# Application logs
aws logs tail /ecs/ollama-api --follow

# Deployment logs
./scripts/deploy.sh staging --dry-run
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to staging
        run: ./scripts/deploy.sh staging
      - name: Run analyzer
        run: |
          cd devops-analyzer
          python devops-analyzer.py deploy --action post-check --cluster staging
```

## 📚 Documentation

- **[Infrastructure Guide](./infra/README.md)** - Detailed infrastructure setup
- **[Application Guide](./src/README.md)** - Application development and API
- **[Analyzer Guide](./devops-analyzer/README.md)** - DevOps analyzer usage
- **[Deployment Guide](./scripts/README.md)** - Deployment scripts and automation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test with `./scripts/deploy.sh staging --dry-run`
5. Submit pull request

## 📄 License

Private project - internal use only.

---

**Ready to automate your DevOps workflow! 🚀**
