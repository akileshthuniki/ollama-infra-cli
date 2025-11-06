# VPC Endpoints for AWS Services
# ECR API endpoint
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-ecr-api-endpoint"
  })
}

# ECR DKR endpoint
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-ecr-dkr-endpoint"
  })
}

# S3 Gateway endpoint (for ECR image layers)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = var.route_table_ids

  tags = merge(var.tags, {
    Name = "${var.project_name}-s3-endpoint"
  })
}

# CloudWatch Logs endpoint
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-logs-endpoint"
  })
}

# Optional: SSM endpoint for ECS Exec
resource "aws_vpc_endpoint" "ssm" {
  count = var.enable_ecs_exec ? 1 : 0

  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-ssm-endpoint"
  })
}

# Optional: SSM Messages endpoint for ECS Exec
resource "aws_vpc_endpoint" "ssmmessages" {
  count = var.enable_ecs_exec ? 1 : 0

  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.project_name}-ssmmessages-endpoint"
  })
}
