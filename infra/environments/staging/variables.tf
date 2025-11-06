# ==========================================
# PROJECT BASICS
# ==========================================
variable "project_name" {
  description = "Name of your project (e.g., 'my-app')"
  type        = string
}

variable "region" {
  description = "AWS region (e.g., 'us-east-1')"
  type        = string
}

variable "tags" {
  description = "Tags to label all resources"
  type        = map(string)
  default = {
    Environment = "staging"
    Terraform   = "true"
  }
}

# ==========================================
# NETWORK CONFIGURATION
# ==========================================
variable "vpc_cidr" {
  description = "IP range for your VPC (e.g., '10.0.0.0/16')"
  type        = string
}

variable "availability_zones" {
  description = "AWS availability zones (e.g., ['us-east-1a', 'us-east-1b'])"
  type        = list(string)
}

# ==========================================
# CONTAINER IMAGES
# ==========================================
variable "api_image_url" {
  description = "Your Docker image URL from ECR"
  type        = string
}

# ==========================================
# API SERVICE SETTINGS
# ==========================================
variable "container_port" {
  description = "Port your API listens on (usually 3000)"
  type        = number
  default     = 3000
}

variable "api_port" {
  description = "Port your API listens on"
  type        = number
  default     = 3000
}

variable "api_cpu" {
  description = "CPU units for the API task"
  type        = string
  default     = "512"
}

variable "api_memory" {
  description = "Memory for the API task in MiB"
  type        = string
  default     = "1024"
}

variable "api_desired_count" {
  description = "Number of API tasks to run"
  type        = number
  default     = 1
}

# ==========================================
# OLLAMA SERVICE SETTINGS
# ==========================================
variable "ollama_image" {
  description = "Ollama container image"
  type        = string
  default     = "ollama/ollama:latest"
}

variable "ollama_port" {
  description = "Port for the Ollama service"
  type        = number
  default     = 11434
}

variable "ollama_cpu" {
  description = "CPU units for the Ollama task"
  type        = string
  default     = "2048"
}

variable "ollama_memory" {
  description = "Memory for the Ollama task in MiB"
  type        = string
  default     = "4096"
}

variable "ollama_desired_count" {
  description = "Number of Ollama tasks to run"
  type        = number
  default     = 1
}

variable "ollama_models" {
  description = "Comma-separated list of Ollama models to automatically pull on startup (e.g., 'llama3.2,llama3.1')"
  type        = string
  default     = "llama3.2"
}

# ==========================================
# ECR SETTINGS
# ==========================================
variable "ecr_image_tag_mutability" {
  description = "ECR image tag mutability"
  type        = string
  default     = "MUTABLE"
}

variable "ecr_image_retention_count" {
  description = "Number of images to retain in ECR"
  type        = number
  default     = 10
}

# ==========================================
# LOGGING SETTINGS
# ==========================================
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# ==========================================
# NETWORKING SETTINGS
# ==========================================
variable "assign_public_ip" {
  description = "Assign public IP to tasks"
  type        = bool
  default     = false
}

# ==========================================
# ECS EXEC SETTINGS
# ==========================================
variable "enable_ecs_exec" {
  description = "Enable ECS Exec for debugging"
  type        = bool
  default     = false
}

# ==========================================
# HEALTH CHECK SETTINGS
# ==========================================
variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "health_check_retries" {
  description = "Health check retries"
  type        = number
  default     = 3
}

variable "health_check_start_period" {
  description = "Health check start period in seconds"
  type        = number
  default     = 60
}
