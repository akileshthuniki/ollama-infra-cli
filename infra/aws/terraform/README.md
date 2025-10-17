# Terraform for ECS Fargate (staging)

This folder contains a minimal Terraform setup that creates an ECR repo and an ECS Fargate service behind an ALB.

Before running, set these variables (example via CLI or CI):
- project
- region
- image_uri
- vpc_id
- public_subnets (list)
- private_subnets (list)
- security_groups (list)

CI will call `terraform apply -var image_uri=...` from the repo root.
# Minimal ECS Fargate with ALB (Terraform)

## Prereqs
- Terraform >= 1.5
- AWS credentials configured (profile or env vars)

## Variables
- `project` (string): name prefix for resources
- `region` (string, default `us-east-1`)
- `image_uri` (string): ECR image to deploy (repo:tag)

## Usage
```bash
cd infra/aws/terraform
terraform init
terraform apply -auto-approve \
  -var project=hello \
  -var region=us-east-1 \
  -var image_uri=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/hello:latest
```

Outputs:
- `alb_url`: app URL via ALB
- `ecr_repository_url`: ECR repo to push images
