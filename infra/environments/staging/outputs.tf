# ==========================================
# USEFUL OUTPUTS AFTER DEPLOYMENT
# ==========================================

# VPC Information
output "vpc_id" {
  description = "Your VPC ID"
  value       = module.vpc.vpc_id
}

# ECS Cluster
output "cluster_name" {
  description = "Your ECS cluster name"
  value       = module.ecs_cluster.cluster_name
}

# Service
output "api_service" {
  description = "API service name (contains both Ollama and Flask in sidecar pattern)"
  value       = module.api_service.service_name
}

# Load Balancer
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer - use this URL to access your API"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  description = "Full URL to access your API"
  value       = "http://${module.alb.alb_dns_name}"
}

# ECR Repositories
output "api_ecr_url" {
  description = "Push your API Docker image here"
  value       = module.ecr_api.repository_url
}

output "ollama_ecr_url" {
  description = "Push your Ollama Docker image here"
  value       = module.ecr_ollama.repository_url
}

# CloudWatch Logs
output "api_logs" {
  description = "View API logs here"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#logsV2:log-groups/log-group/${aws_cloudwatch_log_group.api.name}"
}

output "ollama_logs" {
  description = "View Ollama logs here"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#logsV2:log-groups/log-group/${aws_cloudwatch_log_group.ollama.name}"
}
