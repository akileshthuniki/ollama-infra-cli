# Infrastructure as Code

> **Enterprise-grade AWS infrastructure** managed with Terraform. Supports multi-environment deployments with modular architecture.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Module Structure](#module-structure)
- [Outputs](#outputs)
- [Management](#management)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Cost Management](#cost-management)
- [CI/CD Integration](#cicd-integration)

---

## 🎯 Overview

This infrastructure provides a complete AWS-based containerized application platform using:

- **Amazon ECS** - Container orchestration for scalable microservices
- **Application Load Balancer** - High-availability traffic distribution
- **Amazon VPC** - Isolated network environment with public/private subnets
- **Amazon ECR** - Private container registry
- **CloudWatch** - Centralized logging and monitoring
- **IAM** - Secure role-based access control
- **VPC Endpoints** - Private connectivity to AWS services

### Key Features

✅ **Multi-environment support** - Staging and production environments  
✅ **Modular architecture** - Reusable Terraform modules  
✅ **High availability** - Multi-AZ deployment  
✅ **Security-first** - Private subnets, security groups, IAM roles  
✅ **Observability** - CloudWatch logs and Container Insights  
✅ **Cost-optimized** - Efficient resource allocation  

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Load Balancer (ALB)                │
│              Public Subnet (Multi-AZ)                       │
└──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ECS Service (Fargate)                    │
│              Private Subnet (Multi-AZ)                      │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Flask API       │◄────►│  Ollama (AI)     │            │
│  │  Container       │      │  Container       │            │
│  └──────────────────┘      └──────────────────┘            │
└──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    VPC Endpoints                            │
│  • ECR (Docker Registry)                                    │
│  • CloudWatch Logs                                          │
│  • SSM (Systems Manager)                                     │
│  • S3 (Storage)                                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | Description | Purpose |
|-----------|-------------|---------|
| **VPC** | Virtual Private Cloud | Isolated network environment |
| **Public Subnets** | Internet-facing subnets | ALB and NAT Gateway |
| **Private Subnets** | Internal subnets | ECS tasks (no direct internet) |
| **NAT Gateway** | Network Address Translation | Outbound internet for private subnets |
| **Internet Gateway** | Internet connectivity | Public subnet internet access |
| **ECS Cluster** | Container orchestration | Manages containerized workloads |
| **ECS Service** | Service definition | Runs API and Ollama containers |
| **ALB** | Application Load Balancer | Distributes traffic, SSL termination |
| **ECR** | Container Registry | Stores Docker images |
| **CloudWatch** | Logging & Monitoring | Centralized logs and metrics |
| **IAM Roles** | Access control | Secure permissions for services |
| **Security Groups** | Network firewall | Controls traffic flow |
| **VPC Endpoints** | Private AWS access | Secure access to AWS services |

---

## 🔧 Prerequisites

### Required Tools

- **Terraform** >= 1.0
- **AWS CLI** >= 2.0
- **Docker** (for building images)
- **Git** (for version control)

### AWS Requirements

- **AWS Account** with appropriate permissions
- **AWS CLI configured** with credentials
- **S3 bucket** for Terraform state (configured in `backend.tf`)
- **IAM permissions** for creating resources

### Verify Prerequisites

```bash
# Check Terraform
terraform version

# Check AWS CLI
aws --version

# Verify AWS credentials
aws sts get-caller-identity

# Check Docker
docker --version
```

---

## 🚀 Quick Start

### 1. Configure Environment Variables

```bash
cd infra/environments/staging
```

Edit `staging.tfvars` with your values:

```hcl
project_name = "ollama"
region = "us-east-1"
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]
api_image_url = "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ollama-api:latest"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review Plan

```bash
terraform plan -var-file=staging.tfvars
```

### 4. Deploy

```bash
terraform apply -var-file=staging.tfvars
```

### 5. Get Outputs

```bash
terraform output
```

---

## 📦 Deployment

### Using Deployment Script

```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production

# Deploy with DevOps analyzer
./scripts/deploy.sh staging --with-analyzer
```

### Manual Deployment

#### Step 1: Navigate to Environment

```bash
cd infra/environments/staging
```

#### Step 2: Initialize Terraform

```bash
terraform init
```

This will:
- Download provider plugins
- Initialize S3 backend for state storage
- Download module dependencies

#### Step 3: Plan Changes

```bash
terraform plan -var-file=staging.tfvars
```

Review the execution plan to see what will be created.

#### Step 4: Apply Changes

```bash
terraform apply -var-file=staging.tfvars
```

Type `yes` when prompted, or use `-auto-approve` flag.

#### Step 5: Verify Deployment

```bash
# Check outputs
terraform output

# Test ALB endpoint
curl $(terraform output -raw alb_url)/health
```

### Destroy Infrastructure

```bash
# Destroy staging environment
cd infra/environments/staging
terraform destroy -var-file=staging.tfvars

# Or use script
./scripts/destroy.sh staging
```

⚠️ **Warning**: This will permanently delete all resources. Ensure you have backups if needed.

---

## ⚙️ Configuration

### Environment Structure

```
infra/
├── environments/
│   ├── staging/
│   │   ├── main.tf           # Main infrastructure configuration
│   │   ├── variables.tf      # Variable definitions
│   │   ├── outputs.tf        # Output values
│   │   ├── backend.tf        # State backend configuration
│   │   └── staging.tfvars    # Environment-specific values
│   └── production/           # Production environment (similar structure)
└── modules/
    ├── vpc/                  # VPC networking module
    ├── ecs-cluster/          # ECS cluster module
    ├── ecs-service/          # ECS service module
    ├── alb/                  # Application Load Balancer module
    ├── ecr/                  # ECR repository module
    ├── iam/                  # IAM roles module
    ├── security-group/       # Security groups module
    ├── vpc-endpoints/        # VPC endpoints module
    └── cloudwatch/           # CloudWatch module
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `project_name` | Project identifier (lowercase, no spaces) | `"ollama"` |
| `region` | AWS region | `"us-east-1"` |
| `vpc_cidr` | VPC IP address range | `"10.0.0.0/16"` |
| `availability_zones` | AWS availability zones | `["us-east-1a", "us-east-1b"]` |
| `api_image_url` | Docker image URL for API | `"ACCOUNT.dkr.ecr.REGION.amazonaws.com/ollama-api:TAG"` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `api_port` | API container port | `8080` |
| `api_desired_count` | Number of API tasks | `1` |
| `ollama_port` | Ollama container port | `11434` |
| `ollama_image` | Ollama Docker image | `"ollama/ollama:latest"` |
| `log_retention_days` | CloudWatch log retention | `30` |
| `enable_ecs_exec` | Enable ECS Exec | `true` |
| `assign_public_ip` | Assign public IP to tasks | `false` |

### Example Configuration

```hcl
# staging.tfvars
project_name = "ollama"
region = "us-east-1"
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# Docker Images
api_image_url = "821368347884.dkr.ecr.us-east-1.amazonaws.com/ollama-api:v2"
ollama_image = "821368347884.dkr.ecr.us-east-1.amazonaws.com/ollama-ollama:latest"

# Service Configuration
api_port = 8080
api_desired_count = 1
ollama_port = 11434

# Resource Tags
tags = {
  Project     = "OLLAMA"
  Environment = "staging"
  ManagedBy   = "Terraform"
}

# ECR Settings
ecr_image_tag_mutability = "MUTABLE"
ecr_image_retention_count = 10

# Logging
log_retention_days = 30

# Networking
assign_public_ip = false
enable_ecs_exec = true
```

---

## 📁 Module Structure

### Available Modules

| Module | Purpose | Key Resources |
|-------|---------|---------------|
| **vpc** | Network infrastructure | VPC, Subnets, IGW, NAT Gateway, Route Tables |
| **ecs-cluster** | Container orchestration | ECS Cluster with Container Insights |
| **ecs-service** | Service definition | ECS Service, Task Definition |
| **alb** | Load balancing | Application Load Balancer, Target Group, Listener |
| **ecr** | Container registry | ECR Repository, Lifecycle Policy |
| **iam** | Access control | IAM Roles, Policies for ECS tasks |
| **security-group** | Network security | Security Groups with ingress/egress rules |
| **vpc-endpoints** | Private AWS access | VPC Endpoints for ECR, CloudWatch, SSM, S3 |
| **cloudwatch** | Monitoring | CloudWatch Log Groups |

### Module Usage Example

```hcl
module "vpc" {
  source = "../../modules/vpc"

  name               = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  tags               = var.tags
}
```

---

## 📤 Outputs

After deployment, Terraform outputs useful information:

### View All Outputs

```bash
terraform output
```

### Key Outputs

| Output | Description | Example |
|--------|-------------|---------|
| `alb_url` | Full API URL | `http://ollama-alb-123456.us-east-1.elb.amazonaws.com` |
| `alb_dns_name` | ALB DNS name | `ollama-alb-123456.us-east-1.elb.amazonaws.com` |
| `cluster_name` | ECS cluster name | `ollama-cluster` |
| `api_service` | ECS service name | `ollama-api` |
| `vpc_id` | VPC identifier | `vpc-0123456789abcdef0` |
| `api_ecr_url` | ECR repository URL | `ACCOUNT.dkr.ecr.REGION.amazonaws.com/ollama-api` |
| `ollama_ecr_url` | Ollama ECR URL | `ACCOUNT.dkr.ecr.REGION.amazonaws.com/ollama-ollama` |
| `api_logs` | CloudWatch logs URL | Link to API logs in console |
| `ollama_logs` | Ollama logs URL | Link to Ollama logs in console |

### Use Outputs in Scripts

```bash
# Get ALB URL
ALB_URL=$(terraform output -raw alb_url)
curl $ALB_URL/health

# Get cluster name
CLUSTER=$(terraform output -raw cluster_name)
aws ecs describe-services --cluster $CLUSTER
```

---

## 🔧 Management

### State Management

#### View State

```bash
# List all resources
terraform state list

# Show specific resource
terraform state show 'module.ecs_cluster.aws_ecs_cluster.this'

# Show resource details
terraform show
```

#### Import Existing Resource

```bash
terraform import 'module.ecs_cluster.aws_ecs_cluster.this' cluster-name
```

#### Move Resources

```bash
terraform state mv 'old_address' 'new_address'
```

#### Remove from State

```bash
terraform state rm 'resource_address'
```

### Update Infrastructure

```bash
# 1. Modify .tf files
vim main.tf

# 2. Review changes
terraform plan -var-file=staging.tfvars

# 3. Apply changes
terraform apply -var-file=staging.tfvars
```

### Refresh State

```bash
# Sync state with actual infrastructure
terraform refresh -var-file=staging.tfvars
```

---

## 🔒 Security

### Network Security

- **Private Subnets**: ECS tasks run in private subnets (no direct internet access)
- **Security Groups**: Restrictive firewall rules (least privilege)
- **NAT Gateway**: Controlled outbound internet access
- **VPC Endpoints**: Private connectivity to AWS services (no internet required)

### IAM Security

- **Least Privilege**: IAM roles have minimal required permissions
- **No Access Keys**: Uses IAM roles for service authentication
- **Separate Roles**: Execution role and task role for different permissions

### Security Groups

| Security Group | Purpose | Ingress | Egress |
|----------------|---------|---------|--------|
| **ALB** | Load balancer | Port 80 from internet | Port 8080 to API SG |
| **API** | Flask API service | Port 8080 from ALB SG | Port 11434 to Ollama SG |
| **Ollama** | AI service | Port 11434 from API SG | All outbound |
| **VPC Endpoints** | AWS service access | Port 443 from VPC | All outbound |

### Best Practices

✅ **Regular audits** of security groups and IAM roles  
✅ **Enable CloudTrail** for API logging  
✅ **Use AWS Secrets Manager** for sensitive data  
✅ **Enable VPC Flow Logs** for network monitoring  
✅ **Regular security updates** for container images  

---

## 📊 Monitoring

### CloudWatch Logs

```bash
# View API logs
aws logs tail /ecs/ollama/api --follow

# View Ollama logs
aws logs tail /ecs/ollama/ollama --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /ecs/ollama/api \
  --filter-pattern "ERROR"
```

### ECS Service Status

```bash
# Get cluster name
CLUSTER=$(terraform output -raw cluster_name)

# Check cluster status
aws ecs describe-clusters --clusters $CLUSTER

# Check service status
aws ecs describe-services \
  --cluster $CLUSTER \
  --services $(terraform output -raw api_service)

# List running tasks
aws ecs list-tasks --cluster $CLUSTER
```

### Load Balancer Health

```bash
# Get target group ARN
TG_ARN=$(aws elbv2 describe-target-groups \
  --names ollama-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Check target health
aws elbv2 describe-target-health --target-group-arn $TG_ARN
```

### Container Insights

Container Insights is enabled by default. View metrics in:
- **AWS Console**: CloudWatch → Container Insights
- **Metrics**: CPU, Memory, Network, Storage

---

## 🚨 Troubleshooting

### Common Issues

#### Terraform State Locked

```bash
# Check who has the lock
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "bucket-name/terraform.tfstate-md5"}}'

# Force unlock (use carefully)
terraform force-unlock LOCK_ID
```

#### Resource Creation Fails

```bash
# Check AWS permissions
aws sts get-caller-identity

# Verify service quotas
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-0263D0A3

# Review detailed error
terraform plan -var-file=staging.tfvars -detailed-exitcode
```

#### ECS Tasks Not Starting

```bash
# Check task definition
aws ecs describe-task-definition \
  --task-definition ollama-api

# Check service events
aws ecs describe-services \
  --cluster ollama-cluster \
  --services ollama-api \
  --query 'services[0].events'

# Check task logs
aws logs tail /ecs/ollama/api --follow
```

#### Can't Connect to Service

```bash
# Verify security groups
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*ollama*"

# Check ALB target health
aws elbv2 describe-target-health \
  --target-group-arn TG_ARN

# Verify VPC routing
aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=VPC_ID"
```

#### VPC Endpoint Issues

```bash
# Check endpoint status
aws ec2 describe-vpc-endpoints \
  --vpc-endpoint-ids vpce-xxxxx

# Verify DNS resolution
nslookup vpce-xxxxx-xxxxx.ecr.us-east-1.vpce.amazonaws.com
```

### Debugging Tips

1. **Enable verbose logging**: `TF_LOG=DEBUG terraform apply`
2. **Check CloudWatch logs** for container errors
3. **Review ECS service events** for deployment issues
4. **Verify IAM permissions** for service roles
5. **Test connectivity** from within VPC using ECS Exec

---

## 💰 Cost Management

### Cost Optimization

- **Use Fargate Spot** for non-critical workloads (up to 70% savings)
- **Right-size containers** based on actual usage
- **Enable auto-scaling** to scale down during low traffic
- **Use NAT Gateway** only when needed (consider NAT Instance for dev)
- **Clean up unused resources** regularly

### Cost Monitoring

```bash
# Get cost and usage
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Tag resources for cost tracking
aws ec2 create-tags \
  --resources i-123456 \
  --tags Key=Project,Value=ollama Key=Environment,Value=staging
```

### Estimated Monthly Costs (Staging)

| Resource | Estimated Cost |
|----------|----------------|
| ECS Fargate (1 task) | ~$15-30 |
| ALB | ~$16 |
| NAT Gateway | ~$32 |
| VPC Endpoints | ~$7-14 |
| CloudWatch Logs | ~$1-5 |
| **Total** | **~$70-100/month** |

---

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]
    paths:
      - 'infra/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Terraform Init
        run: |
          cd infra/environments/staging
          terraform init
      
      - name: Terraform Plan
        run: |
          cd infra/environments/staging
          terraform plan -var-file=staging.tfvars -out=tfplan
      
      - name: Terraform Apply
        run: |
          cd infra/environments/staging
          terraform apply -auto-approve tfplan
```

### GitLab CI

```yaml
deploy_infrastructure:
  stage: deploy
  image: hashicorp/terraform:latest
  before_script:
    - cd infra/environments/staging
    - terraform init
  script:
    - terraform plan -var-file=staging.tfvars
    - terraform apply -auto-approve -var-file=staging.tfvars
  only:
    - main
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Deploy Infrastructure') {
            steps {
                sh '''
                    cd infra/environments/${ENV}
                    terraform init
                    terraform plan -var-file=${ENV}.tfvars
                    terraform apply -auto-approve -var-file=${ENV}.tfvars
                '''
            }
        }
    }
}
```

---

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [VPC Endpoints Guide](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints.html)
- [CloudWatch Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)

---

## 🤝 Contributing

When modifying infrastructure:

1. **Test in staging** first
2. **Review Terraform plan** carefully
3. **Update documentation** for any changes
4. **Tag resources** appropriately
5. **Follow naming conventions**

---

## 📝 License

This infrastructure code is part of the Ollama Infrastructure project.

---

<div align="center">

**Infrastructure managed as code, deployed automatically.** 🚀

[Back to Main README](../README.md)

</div>
