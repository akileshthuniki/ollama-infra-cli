# Infrastructure as Code

AWS infrastructure managed with Terraform. Supports staging and production environments.

## 🏗️ Architecture

### Components
- **VPC** - Private network with public/private subnets
- **ECS Cluster** - Container orchestration for Ollama API
- **Application Load Balancer** - Public-facing load balancer
- **IAM Roles** - Secure permissions for services
- **Security Groups** - Network security rules

### Environment Structure
```
infra/
├── environments/
│   ├── staging/           # Staging environment
│   │   ├── main.tf       # Main configuration
│   │   ├── variables.tf  # Input variables
│   │   └── terraform.tfvars # Environment variables
│   └── production/        # Production environment
│       ├── main.tf       # Main configuration
│       ├── variables.tf  # Input variables
│       └── terraform.tfvars # Environment variables
└── modules/
    ├── vpc/              # VPC networking module
    ├── ecs/              # ECS cluster module
    └── alb/              # Load balancer module
```

## 🚀 Deployment

### Quick Deploy
```bash
# Deploy staging
./scripts/deploy.sh staging

# Deploy production
./scripts/deploy.sh production
```

### Manual Deploy
```bash
# Navigate to environment
cd infra/environments/staging

# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply
```

## ⚙️ Configuration

### Required Variables
- `region` - AWS region
- `project_name` - Project identifier
- `environment` - Environment name (staging/production)

### Optional Variables
- `vpc_cidr` - VPC IP range
- `instance_count` - Number of ECS instances
- `instance_type` - EC2 instance type

### Example terraform.tfvars
```hcl
region = "us-east-1"
project_name = "ollama-infra"
environment = "staging"
vpc_cidr = "10.0.0.0/16"
instance_count = 2
instance_type = "t3.medium"
```

## 🔧 Management

### View Resources
```bash
# List all resources
terraform state list

# Show specific resource
terraform state show 'aws_ecs_cluster.main'

# Import existing resource
terraform import aws_ecs_cluster.main cluster-name
```

### Destroy Infrastructure
```bash
# Destroy specific environment
cd infra/environments/staging
terraform destroy

# Or use script
./scripts/destroy.sh staging
```

### Update Infrastructure
```bash
# Make changes to .tf files
cd infra/environments/staging

# Plan changes
terraform plan

# Apply changes
terraform apply
```

## 📊 Monitoring

### Check Status
```bash
# ECS cluster status
aws ecs describe-clusters --clusters ollama-cluster-staging

# Service status
aws ecs describe-services --cluster ollama-cluster-staging --services ollama-api

# Load balancer status
aws elbv2 describe-load-balancers --names ollama-alb-staging
```

### View Logs
```bash
# ECS service logs
aws logs tail /ecs/ollama-api-staging --follow

# Task logs
aws logs tail /ecs/ollama-api-staging --filter-pattern "ERROR"
```

## 🔒 Security

### Network Security
- Private subnets for application instances
- Security groups restrict traffic to necessary ports
- ALB handles public traffic, instances stay private

### IAM Security
- Least privilege IAM roles
- Service-specific permissions
- No access keys stored in code

### Best Practices
- Regular security group audits
- IAM role reviews
- Network ACL monitoring

## 🚨 Troubleshooting

### Common Issues

**Terraform state locked?**
```bash
# Force unlock (use carefully)
terraform force-unlock LOCK_ID

# Or check who has it locked
terraform force-unlock --help
```

**Resource creation fails?**
```bash
# Check AWS permissions
aws sts get-caller-identity

# Check service limits
aws service-quotas list-services

# Review error logs
cd infra/environments/staging
terraform plan -detailed-exitcode
```

**Can't connect to services?**
```bash
# Check security groups
aws ec2 describe-security-groups --filters Name=group-name,Values=*staging*

# Check load balancer
aws elbv2 describe-target-health --target-group-arn TG_ARN

# Check VPC routing
aws ec2 describe-route-tables --filters Name=vpc-id,Values=VPC_ID
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
- name: Deploy Infrastructure
  run: |
    cd infra/environments/staging
    terraform init
    terraform plan -out=terraform.tfplan
    terraform apply -auto-approve terraform.tfplan
```

### Jenkins Pipeline
```groovy
stage('Deploy Infrastructure') {
    steps {
        sh '''
            cd infra/environments/${ENV}
            terraform init
            terraform apply -auto-approve
        '''
    }
}
```

## 📈 Cost Management

### Monitor Costs
```bash
# Cost Explorer
aws ce get-cost-and-usage --time-period Start=2023-01-01,End=2023-01-31

# Tag resources for cost tracking
aws ec2 create-tags --resources i-123456 --tags Key=Project,Value=ollama-infra
```

### Optimize Costs
- Use appropriate instance sizes
- Enable auto-scaling
- Monitor unused resources
- Use spot instances for non-critical workloads

## 🧪 Testing

### Test Infrastructure
```bash
# Validate Terraform code
terraform validate

# Check formatting
terraform fmt -check

# Security scan
terraform fmt -check && terraform validate
```

### Test Deployment
```bash
# Deploy to test environment
./scripts/deploy.sh test

# Run health checks
./scripts/health-check.sh test

# Clean up test environment
./scripts/destroy.sh test
```

---

**Infrastructure managed as code, deployed automatically.** 🚀
