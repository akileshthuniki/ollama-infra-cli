# DevOps Infrastructure & Analysis Suite

> **Enterprise-grade DevOps toolkit** with infrastructure automation, private AI services, and intelligent analysis tools for modern cloud operations.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Terraform](https://img.shields.io/badge/Terraform-1.0+-623CE4.svg)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-ECS-FF9900.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Documentation](#-documentation)
- [CI/CD Integration](#-cicd-integration)
- [Monitoring & Observability](#-monitoring--observability)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This comprehensive DevOps suite provides:

- **🏗️ Infrastructure as Code** - Automated AWS infrastructure deployment using Terraform
- **🤖 Private AI Service** - Self-hosted Ollama-based AI inference for DevOps analysis
- **🔍 DevOps Analyzer** - Intelligent CLI tool for URL analysis, infrastructure health checks, and deployment validation
- **🚀 CI/CD Integration** - Ready-to-use automation scripts and GitHub Actions workflows
- **📊 Monitoring & Observability** - Built-in health checks, logging, and analysis capabilities

### Key Benefits

✅ **Privacy-First** - All AI processing happens on your infrastructure  
✅ **Production-Ready** - Battle-tested deployment scripts and configurations  
✅ **Developer-Friendly** - Simple CLI interface with intelligent fallbacks  
✅ **Comprehensive** - End-to-end solution from infrastructure to analysis  
✅ **Extensible** - Modular design for easy customization

---

## 🏗️ Architecture

```
     ┌─────────────────────────────────────────────────────────────┐
     │                    DevOps Infrastructure Suite              │
     └─────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼───────────────────────┐
        │                         │                       │
   ┌────▼──────────┐        ┌─────▼──────┐         ┌──────▼──────┐
   │  Terraform    │        │   ECS      │         │   DevOps    │
   │ Infrastructure│        │  Services  │         │  Analyzer   │
   │   (IaC)       │        │            │         │   (CLI)     │
   └───────────────┘        └────────────┘         └─────────────┘
        │                         │                       │
        │                  ┌──────▼───────┐               │
        │                  │ Application  │               │
        │                  │ Load Balancer│               │
        │                  └──────┬───────┘                │
        │                         │                       │
        └─────────────────────────┼───────────────────────┘
                                  │
                        ┌─────────▼─────────┐
                        │  Ollama AI Service│
                        │  (Private AI)     │
                        └───────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Infrastructure** | Terraform | AWS ECS, ALB, VPC, IAM provisioning |
| **Container Orchestration** | AWS ECS Fargate | Scalable container deployment |
| **AI Service** | Flask + Ollama | Private AI inference API |
| **Analysis Tool** | Python CLI | URL analysis, infrastructure health checks |
| **Load Balancing** | AWS ALB | Traffic distribution and health checks |

---

## ✨ Features

### 🏗️ Infrastructure Automation

- **Multi-Environment Support** - Staging and production environments
- **Infrastructure as Code** - Version-controlled Terraform configurations
- **Automated Deployment** - One-command deployment scripts
- **Security Best Practices** - IAM roles, security groups, VPC isolation
- **Scalability** - Auto-scaling ECS services with load balancing

### 🤖 Private AI Service

- **Self-Hosted AI** - Ollama-based inference on your infrastructure
- **RESTful API** - Flask-based API gateway
- **Health Monitoring** - Built-in health checks and readiness probes
- **Model Management** - Support for multiple AI models (Llama, Mistral, etc.)
- **Production-Ready** - Gunicorn, Prometheus metrics, structured logging

### 🔍 DevOps Analyzer

- **URL Analysis** - Comprehensive connectivity and performance testing
- **Infrastructure Health** - AWS ECS cluster and service health monitoring
- **Deployment Validation** - Pre and post-deployment checks
- **AI-Powered Insights** - Intelligent analysis with fallback support
- **Question-Based Queries** - Natural language questions for specific analysis

### 📊 Key Capabilities

- ✅ DNS resolution testing
- ✅ SSL/TLS certificate validation
- ✅ HTTP/HTTPS connectivity checks
- ✅ Response time measurement
- ✅ Service health monitoring
- ✅ Architecture documentation
- ✅ Security auditing
- ✅ Performance analysis

---

## 🚀 Quick Start

### Prerequisites

- **AWS Account** with appropriate permissions
- **AWS CLI** configured (`aws configure`)
- **Terraform** >= 1.0
- **Docker** (for local development)
- **Python** 3.7+ (for DevOps Analyzer)

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/akileshthuniki/ollama-infra-cli.git
cd ollama-infra-cli

# 2. Deploy infrastructure to staging
./scripts/deploy.sh staging

# 3. Test the deployment
curl https://your-alb-url.amazonaws.com/health

# 4. Use DevOps Analyzer
cd devops-analyzer
pip install -r requirements.txt
python devops-analyzer.py url <Your-cluster-url/alb/Other URL> --question "Is this secure?"
```

---

## 📦 Installation

### Infrastructure Setup

```bash
# Install Terraform (if not installed)
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
```

### DevOps Analyzer Setup

```bash
cd devops-analyzer

# Install dependencies
pip install -r requirements.txt

# Verify installation
python devops-analyzer.py --help
```

### AWS Configuration

```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity

# Set environment variables
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
```

---

## 📖 Usage

### Infrastructure Deployment

#### Deploy to Staging

```bash
# Full deployment
./scripts/deploy.sh staging

# Deployment with analyzer
./scripts/deploy.sh staging --with-analyzer

# Dry run (preview changes)
./scripts/deploy.sh staging --dry-run
```

#### Deploy to Production

```bash
# Production deployment (requires confirmation)
./scripts/deploy.sh production

# With specific configuration
./scripts/deploy.sh production --config config/production.yaml
```

### DevOps Analyzer

#### URL Analysis

```bash
# Basic connectivity check
python devops-analyzer.py url https://api.example.com

# Performance analysis
python devops-analyzer.py url https://api.example.com \
  --question "Why is this slow? How can I improve performance?"

# Security audit
python devops-analyzer.py url https://api.example.com \
  --question "Is this secure? Are there any security issues?" \
  --output security-report.md

# Availability check
python devops-analyzer.py url https://my-alb.amazonaws.com \
  --question "How can I improve availability?"
```

#### Infrastructure Analysis

```bash
# Architecture documentation
python devops-analyzer.py infrastructure \
  --type architecture \
  --cluster production \
  --output architecture.md

# Health check
python devops-analyzer.py infrastructure \
  --type health \
  --cluster production \
  --service api-service

# Multi-service health check
python devops-analyzer.py infrastructure \
  --type health \
  --cluster production
```

#### Deployment Validation

```bash
# Pre-deployment check
python devops-analyzer.py deploy \
  --action pre-check \
  --cluster production \
  --service api-service

# Post-deployment verification
python devops-analyzer.py deploy \
  --action post-check \
  --cluster production \
  --service api-service
```

### API Usage

#### Health Check

```bash
# Basic health check
curl https://your-alb-url.amazonaws.com/health

# Detailed health information
curl https://your-alb-url.amazonaws.com/health/ready
```

#### AI Analysis API

```bash
# AI-powered analysis
curl -X POST https://your-alb-url.amazonaws.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze this infrastructure and provide recommendations",
    "context": "aws-infrastructure"
  }'

# List available models
curl https://your-alb-url.amazonaws.com/api/models
```

---

## 📚 Documentation

### Core Documentation

| Document | Description | Link |
|----------|-------------|------|
| **Main README** | This file - project overview and quick start | [README.md](./README.md) |
| **Infrastructure Guide** | Detailed infrastructure setup and configuration | [infra/README.md](./infra/README.md) |
| **Application Guide** | Flask application development and API reference | [src/README.md](./src/README.md) |
| **Deployment Guide** | Deployment scripts and automation | [scripts/README.md](./scripts/README.md) |

### DevOps Analyzer Documentation

| Document | Description | Link |
|----------|-------------|------|
| **Analyzer README** | DevOps Analyzer overview and installation | [devops-analyzer/README.md](./devops-analyzer/README.md) |
| **Daily Scenarios** | Real-world DevOps engineer scenarios and usage examples | [devops-analyzer/DEVOPS_DAILY_SCENARIOS.md](./devops-analyzer/DEVOPS_DAILY_SCENARIOS.md) |
| **Installation Guide** | Detailed installation instructions | [devops-analyzer/INSTALL.md](./devops-analyzer/INSTALL.md) |

### Configuration Files

- `config/staging.yaml` - Staging environment configuration
- `config/production.yaml` - Production environment configuration
- `infra/environments/staging/terraform.tfvars` - Terraform variables
- `infra/environments/production/terraform.tfvars` - Production Terraform variables

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Deploy and Validate

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  pre-deployment-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          cd devops-analyzer
          pip install -r requirements.txt
          
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Pre-deployment validation
        run: |
          python devops-analyzer.py deploy \
            --action pre-check \
            --cluster ${{ env.CLUSTER }} \
            --service ${{ env.SERVICE }}
        env:
          CLUSTER: production
          SERVICE: api-service
          
  deploy:
    needs: pre-deployment-check
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Deploy infrastructure
        run: ./scripts/deploy.sh production
        
      - name: Post-deployment verification
        run: |
          cd devops-analyzer
          pip install -r requirements.txt
          python devops-analyzer.py deploy \
            --action post-check \
            --cluster production \
            --service api-service
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        CLUSTER = 'production'
    }
    
    stages {
        stage('Pre-Deployment Check') {
            steps {
                sh '''
                    cd devops-analyzer
                    pip install -r requirements.txt
                    python devops-analyzer.py deploy \
                        --action pre-check \
                        --cluster ${CLUSTER}
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh './scripts/deploy.sh production'
            }
        }
        
        stage('Post-Deployment Verification') {
            steps {
                sh '''
                    cd devops-analyzer
                    python devops-analyzer.py deploy \
                        --action post-check \
                        --cluster ${CLUSTER}
                '''
            }
        }
    }
}
```

---

## 📊 Monitoring & Observability

### Health Checks

```bash
# Infrastructure health
python devops-analyzer.py infrastructure \
  --type health \
  --cluster production

# Service health via API
curl https://your-alb-url.amazonaws.com/health/ready

# URL health check
python devops-analyzer.py url https://api.example.com/health \
  --question "Is everything working correctly?"
```

### Logging

```bash
# Application logs
aws logs tail /ecs/ollama-api --follow

# Filtered logs
aws logs tail /ecs/ollama-api --filter-pattern "ERROR"

# Infrastructure logs
aws logs tail /ecs/ollama-api-staging --follow
```

### Metrics

- **Prometheus Metrics** - Available at `/metrics` endpoint
- **CloudWatch Metrics** - Automatic ECS service metrics
- **Custom Metrics** - Application-specific metrics via Prometheus

### Alerting Integration

```bash
#!/bin/bash
# alert_handler.sh - Integrate with Prometheus/Alertmanager

ALERT_URL=$1
ALERT_NAME=$2

# Generate analysis
python devops-analyzer.py url $ALERT_URL \
  --question "What is causing this alert? How can I fix it?" \
  --output "alerts/$(date +%Y%m%d_%H%M%S)_${ALERT_NAME}.md"

# Send to notification system
# Add your Slack/Teams/PagerDuty integration here
```

---

## 🔧 Troubleshooting

### Common Issues

#### Deployment Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Terraform state
cd infra/environments/staging
terraform plan

# Check IAM permissions
aws iam get-user
```

#### Service Not Responding

```bash
# Check service logs
aws logs tail /ecs/ollama-api --follow

# Verify service health
python devops-analyzer.py infrastructure \
  --type health \
  --cluster production

# Test connectivity
python devops-analyzer.py url https://your-alb-url.amazonaws.com \
  --question "Why is this not responding?"
```

#### DevOps Analyzer Issues

```bash
# Test without AI (faster, uses fallback)
python devops-analyzer.py url https:api-example.com --no-ai

# Check API connectivity
curl -I http://your-ollama-api:11434/api/tags

# Verify dependencies
pip list | grep -E "requests|boto3"
```

#### SSL Certificate Issues

```bash
# Check SSL certificate
python devops-analyzer.py url https://api.example.com \
  --question "Is the SSL certificate valid?"

# Test certificate expiration
openssl s_client -connect api.example.com:443 -servername api.example.com
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Run with debug output
python devops-analyzer.py url https://api.example.com --no-ai
```

---

## 🏗️ Project Structure

```
.
├── 📄 README.md                          # This file - main documentation
├── 🚀 scripts/                           # Deployment and utility scripts
│   ├── deploy.sh                        # Main deployment script
│   └── README.md                        # Deployment documentation
├── 🏗️ infra/                             # Infrastructure as Code
│   ├── environments/                    # Environment-specific configs
│   │   ├── staging/                    # Staging environment
│   │   └── production/                 # Production environment
│   ├── modules/                         # Reusable Terraform modules
│   └── README.md                        # Infrastructure documentation
├── 🤖 src/                               # Application source code
│   ├── app.py                          # Flask application
│   └── README.md                       # Application documentation
├── 🔍 devops-analyzer/                   # DevOps Analyzer CLI tool
│   ├── devops-analyzer.py              # Main analyzer tool
│   ├── README.md                       # Analyzer documentation
│   ├── DEVOPS_DAILY_SCENARIOS.md      # Real-world scenarios
│   ├── INSTALL.md                      # Installation guide
│   └── requirements.txt                # Python dependencies
├── 🐳 docker/                            # Docker configurations
│   ├── Dockerfile.ollama               # Ollama container
│   └── Dockerfile.api                 # API container
├── ⚙️ config/                            # Configuration files
│   ├── staging.yaml                    # Staging config
│   └── production.yaml                 # Production config
└── 📚 docs/                             # Additional documentation
```

---

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
   ```bash
   # Test infrastructure changes
   ./scripts/deploy.sh staging --dry-run
   
   # Test analyzer changes
   cd devops-analyzer
   python devops-analyzer.py url https://google.com --no-ai
   ```
5. **Submit a pull request**

### Code Standards

- **Python**: Follow PEP 8 style guide
- **Terraform**: Use `terraform fmt` for formatting
- **Documentation**: Update relevant README files
- **Testing**: Include tests for new features

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No breaking changes (or documented)
- [ ] Reviewed by at least one team member

---

## 📄 License

**Proprietary** - Internal use only. All rights reserved.

This project is proprietary software. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited.

---

## Acknowledgments

- **Ollama** - For providing the private AI inference framework
- **Terraform** - For infrastructure as code capabilities
- **AWS** - For cloud infrastructure services
- **Flask** - For the lightweight web framework

---

## Support

For issues, questions, or contributions:

- **Documentation**: See [Documentation](#-documentation) section above
- **Issues**: Create an issue in the repository
- **Questions**: Refer to troubleshooting section or relevant documentation

---

## Quick Links

- [Infrastructure Guide](./infra/README.md)
- [Application Guide](./src/README.md)
- [DevOps Analyzer Guide](./devops-analyzer/README.md)
- [Daily Scenarios](./devops-analyzer/DEVOPS_DAILY_SCENARIOS.md)
- [Installation Guide](./devops-analyzer/INSTALL.md)
- [Deployment Guide](./scripts/README.md)

---

<div align="center">

**Built with ❤️ for DevOps Engineers**

*Automating infrastructure, empowering analysis, enabling innovation.*

</div>