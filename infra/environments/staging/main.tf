# ==========================================
# AWS Provider Configuration
# ==========================================
provider "aws" {
  region = var.region
}

# ==========================================
# NETWORKING - VPC, Subnets, Internet Access
# ==========================================
module "vpc" {
  source = "../../modules/vpc"

  name               = var.project_name
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  tags               = var.tags
}

# ==========================================
# ECR - Container Registry
# ==========================================
module "ecr_api" {
  source = "../../modules/ecr"

  repository_name         = "${var.project_name}-api"
  image_tag_mutability    = var.ecr_image_tag_mutability
  image_retention_count   = var.ecr_image_retention_count
  tags                    = var.tags
}

module "ecr_ollama" {
  source = "../../modules/ecr"

  repository_name         = "${var.project_name}-ollama"
  image_tag_mutability    = var.ecr_image_tag_mutability
  image_retention_count   = var.ecr_image_retention_count
  tags                    = var.tags
}

# ==========================================
# LOGGING - CloudWatch Log Groups
# ==========================================
resource "aws_cloudwatch_log_group" "ollama" {
  name              = "/ecs/${var.project_name}/ollama"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}/api"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

# ==========================================
# IAM ROLES - Permissions for ECS Tasks
# ==========================================
module "iam" {
  source = "../../modules/iam"

  project_name    = var.project_name
  log_group_arns  = ["${aws_cloudwatch_log_group.ollama.arn}:*", "${aws_cloudwatch_log_group.api.arn}:*"]
  enable_ecs_exec = var.enable_ecs_exec
  tags            = var.tags
}

# ==========================================
# ECS CLUSTER - Container Orchestration
# ==========================================
module "ecs_cluster" {
  source = "../../modules/ecs-cluster"

  cluster_name              = "${var.project_name}-cluster"
  enable_container_insights = true
  tags                      = var.tags
}

# ==========================================
# VPC ENDPOINTS - Private Access to AWS Services
# ==========================================
# Security group allowing HTTPS traffic for VPC endpoints
module "vpc_endpoint_sg" {
  source = "../../modules/security-group"

  name        = "${var.project_name}-vpc-endpoints"
  description = "Allow HTTPS for VPC endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = [{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from VPC"
  }]

  egress_rules = [{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }]

  tags = var.tags
}

# VPC endpoints for ECR, CloudWatch, S3
module "vpc_endpoints" {
  source = "../../modules/vpc-endpoints"

  project_name       = var.project_name
  vpc_id             = module.vpc.vpc_id
  region             = var.region
  subnet_ids         = module.vpc.private_subnet_ids
  route_table_ids    = [module.vpc.private_route_table_id]
  security_group_ids = [module.vpc_endpoint_sg.security_group_id]
  enable_ecs_exec    = var.enable_ecs_exec
  tags               = var.tags
}

# ==========================================
# SECURITY GROUPS - Firewall Rules
# ==========================================

# Ollama Service Security Group
module "ollama_sg" {
  source = "../../modules/security-group"

  name        = "${var.project_name}-ollama"
  description = "Ollama service - port 11434"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = [{
    from_port                = 11434
    to_port                  = 11434
    protocol                 = "tcp"
    source_security_group_id = module.api_sg.security_group_id
    description              = "Ollama API from API service"
  }]

  egress_rules = [{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }]

  tags = var.tags
}

# API Service Security Group
module "api_sg" {
  source = "../../modules/security-group"

  name        = "${var.project_name}-api"
  description = "API service - port ${var.api_port}"
  vpc_id      = module.vpc.vpc_id

  ingress_rules = [{
    from_port   = var.api_port
    to_port     = var.api_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "API traffic from anywhere"
  }]

  egress_rules = [{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }]

  tags = var.tags
}

# ==========================================
# LOAD BALANCER - Traffic Distribution
# ==========================================
module "alb" {
  source = "../../modules/alb"

  name               = var.project_name
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.public_subnet_ids
  internal           = false
  target_port        = var.api_port
  allowed_cidr_blocks = ["0.0.0.0/0"]

  # Increase idle timeout to handle longer AI requests
  idle_timeout = 300

  # Health check settings
  health_check_path                = "/health"
  health_check_interval            = 30
  health_check_timeout             = 5
  health_check_healthy_threshold   = 2
  health_check_unhealthy_threshold = 3
  health_check_matcher             = "200-299"
  deregistration_delay             = 30

  enable_deletion_protection = false

  tags = var.tags
}

# ==========================================
# API SERVICE - Your Application (with Ollama sidecar)
# ==========================================
module "api_service" {
  source = "../../modules/ecs-service"

  # Basic Configuration
  service_name    = "${var.project_name}-api"
  cluster_id      = module.ecs_cluster.cluster_id
  desired_count   = var.api_desired_count

  # Resources (increased to handle both containers)
  cpu    = "2048"
  memory = "6144"

  # Networking
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [module.api_sg.security_group_id]
  assign_public_ip   = var.assign_public_ip

  # IAM & Logging
  execution_role_arn = module.iam.execution_role_arn
  task_role_arn      = module.iam.task_role_arn
  region             = var.region

  # Load Balancer Configuration
  target_group_arn              = module.alb.target_group_arn
  load_balancer_container_name  = "api"
  load_balancer_container_port  = var.api_port

  # Container Definitions (sidecar pattern)
  container_definitions = [
    {
      name         = "ollama"
      image        = var.ollama_image
      essential    = false  # Ollama is not essential, API can start without it
      portMappings = [
        {
          containerPort = var.ollama_port
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "OLLAMA_MODELS"
          value = var.ollama_models
        },
        {
          name  = "CORS_ENABLED"
          value = "true"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ollama.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
      # Temporarily disable health check for debugging
      # healthCheck = {
      #   command     = ["CMD-SHELL", "curl -f http://localhost:${var.ollama_port}/ || exit 1"]
      #   interval    = 30
      #   timeout     = 5
      #   retries     = 3
      #   startPeriod = 120  # Increased for Ollama initialization
      # }
    },
    {
      name         = "api"
      image        = var.api_image_url
      essential    = true
      portMappings = [
        {
          containerPort = var.api_port
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "OLLAMA_URL"
          value = "http://localhost:${var.ollama_port}"
        },
        {
          name  = "PORT"
          value = tostring(var.api_port)
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
      # Temporarily disable health check for debugging
      # healthCheck = {
      #   command     = ["CMD-SHELL", "curl -f http://localhost:${var.api_port}/health || exit 1"]
      #   interval    = var.health_check_interval
      #   timeout     = var.health_check_timeout
      #   retries     = var.health_check_retries
      #   startPeriod = 180  # Increased to allow Ollama to fully initialize
      # }
      # Temporarily remove dependency for debugging
      # dependsOn = [
      #   {
      #     containerName = "ollama"
      #     condition     = "HEALTHY"  # Wait for Ollama to be healthy before starting API
      #   }
      # ]
    }
  ]

  force_new_deployment = true

  # Force new deployment by updating a tag
  tags = merge(var.tags, {
    DeploymentTimestamp = "2025-11-05-14-10"
  })
  depends_on = [module.vpc_endpoints, module.alb]
}
