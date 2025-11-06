# Deployment Scripts

Automation scripts for deploying and managing the DevOps infrastructure.

## 🚀 Scripts Overview

### deploy.sh
Main deployment script that handles the complete deployment process.

**Features:**
- Builds and pushes Docker images to ECR
- Deploys infrastructure with Terraform
- Performs health checks
- Optional DevOps analyzer integration
- Multi-environment support (staging/production)

## 📖 Usage

### Quick Deploy
```bash
# Deploy to staging (default)
./scripts/deploy.sh

# Deploy to staging explicitly
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Deploy with analyzer
./scripts/deploy.sh staging --with-analyzer
```

### Help
```bash
./scripts/deploy.sh --help
```

## 🔧 Requirements

### Prerequisites
- AWS CLI configured
- Terraform installed
- Docker installed
- Git (for getting commit hash)

### AWS Permissions
Required IAM permissions:
- ECR: Push/pull images
- ECS: Manage clusters and services
- ELB: Manage load balancers
- IAM: Create roles and policies
- VPC: Manage networking

## 📋 Process Flow

1. **Validation** - Check environment and prerequisites
2. **Build** - Build Docker image with git tag
3. **Push** - Push image to ECR registry
4. **Deploy** - Apply Terraform configuration
5. **Health Check** - Verify deployment is healthy
6. **Analysis** - Run DevOps analyzer (optional)
7. **Summary** - Show deployment results

## 🎯 Environment Configuration

### Staging
- Lower resource requirements
- Debug logging enabled
- Faster deployment times

### Production
- High availability configuration
- Comprehensive monitoring
- Slower, safer deployment

## 📊 Output

### Deployment Summary
```
==================================
🎉 Deployment Summary
==================================
Environment: staging
Project: ollama-infra
ALB URL: https://your-alb.amazonaws.com
Health Endpoint: https://your-alb.amazonaws.com/health
API Endpoint: https://your-alb.amazonaws.com/api/analyze
ECS Cluster: ollama-cluster-staging

🔍 Next Steps:
1. Test the API: curl https://your-alb.amazonaws.com/health
2. Check the logs: aws logs tail /ecs/ollama-api-staging --follow
3. Run analyzer: cd devops-analyzer && python devops-analyzer.py infrastructure --type health --cluster ollama-cluster-staging
```

### Analyzer Reports
When using `--with-analyzer`:
- `reports/deployment_analysis_*.md` - URL and deployment analysis
- `reports/health_check_*.md` - Infrastructure health analysis

## 🚨 Troubleshooting

### Common Issues

**AWS credentials not found?**
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**Terraform state locked?**
```bash
cd infra/environments/staging
terraform force-unlock LOCK_ID
```

**Docker build fails?**
```bash
# Check Dockerfile exists
ls -la docker/Dockerfile.api

# Check build context
docker build -f docker/Dockerfile.api .
```

**Health check fails?**
```bash
# Check service logs
aws logs tail /ecs/ollama-api-staging --follow

# Check ECS service status
aws ecs describe-services --cluster ollama-cluster-staging --services ollama-api

# Check load balancer health
aws elbv2 describe-target-health --target-group-arn TG_ARN
```

### Debug Mode
Add debug output by setting environment variable:
```bash
export DEBUG=1
./scripts/deploy.sh staging
```

### Dry Run
To see what would be deployed without actually deploying:
```bash
cd infra/environments/staging
terraform plan
```

## 🔄 Advanced Usage

### Custom Environment Variables
```bash
export AWS_DEFAULT_REGION=us-west-2
export IMAGE_TAG=custom-tag
./scripts/deploy.sh staging
```

### Skip Health Check
Modify the script or use Terraform directly:
```bash
cd infra/environments/staging
terraform apply -auto-approve -var "image_uri=$IMAGE_URI"
```

### Rollback
```bash
cd infra/environments/staging
terraform plan -destroy
terraform apply -destroy
```

## 📈 Monitoring

### During Deployment
- Real-time progress updates
- Colored output for status
- Error handling with clear messages

### Post-Deployment
- Health check verification
- Log monitoring instructions
- Analyzer integration for deep insights

## 🤝 Integration

### CI/CD Pipeline
The script is designed to work with CI/CD systems:
```yaml
- name: Deploy to Staging
  run: ./scripts/deploy.sh staging --with-analyzer
```

### Local Development
```bash
# Quick test deployment
./scripts/deploy.sh staging

# Full production deployment
./scripts/deploy.sh production --with-analyzer
```

---

**Automated deployment made simple and reliable!** 🚀
