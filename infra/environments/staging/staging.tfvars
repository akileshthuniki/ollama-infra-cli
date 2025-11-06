# 1. Project name (no spaces, lowercase)
project_name = "ollama"

# 2. AWS region where to deploy
region = "us-east-1"

# 3. Your Docker image URL (update after pushing to ECR)
api_image_url = "821368347884.dkr.ecr.us-east-1.amazonaws.com/ollama-api:v2"

# 4. VPC network range
vpc_cidr = "10.0.0.0/16"

# 5. Availability zones (use 2 for high availability)
availability_zones = ["us-east-1a", "us-east-1b"]


# Port your API uses (matches Flask app default: 8080)
api_port = 8080

# Resource tags
tags = {
  Project     = "OLLAMA"
  Environment = "staging"
  ManagedBy   = "Terraform"
}

# Ollama Settings (now runs as sidecar in same task)
ollama_port = 11434
ollama_image = "821368347884.dkr.ecr.us-east-1.amazonaws.com/ollama-ollama:latest"  # Custom image with models pre-loaded
ollama_models = "llama3.2"  # Models already included in image

# API Service Settings (now includes both containers in sidecar pattern)
# CPU and memory are allocated at task level (1024 CPU = 1 vCPU, 4096 = 4GB)
api_desired_count = 1

# ECR Settings
ecr_image_tag_mutability = "MUTABLE"
ecr_image_retention_count = 10

# Logging Settings
log_retention_days = 30

# Networking Settings
assign_public_ip = false

# ECS Exec Settings
enable_ecs_exec = true  # Enable to pull Ollama models

# Health Check Settings
# Increased start period to allow Ollama to fully initialize (30-60 seconds)
health_check_interval = 30
health_check_timeout = 30  # Increased for Ollama initialization
health_check_retries = 3
health_check_start_period = 90  # Increased grace period for sidecar startup
