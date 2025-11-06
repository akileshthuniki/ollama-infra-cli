variable "service_name" {
  description = "Name of the ECS service"
  type        = string
}

variable "cluster_id" {
  description = "ID of the ECS cluster"
  type        = string
}

# Container definitions - supports multiple containers for sidecar pattern
variable "container_definitions" {
  description = "List of container definitions for the task"
  type = list(object({
    name         = string
    image        = string
    essential    = bool
    portMappings = list(object({
      containerPort = number
      protocol      = string
    }))
    environment = list(object({
      name  = string
      value = string
    }))
    logConfiguration = object({
      logDriver = string
      options = object({
        awslogs-group         = string
        awslogs-region        = string
        awslogs-stream-prefix = string
      })
    })
    healthCheck = optional(object({
      command     = list(string)
      interval    = number
      timeout     = number
      retries     = number
      startPeriod = number
    }))
    dependsOn = optional(list(object({
      containerName = string
      condition     = string
    })))
  }))
}

# Legacy variables for backward compatibility (will be removed)
variable "container_name" {
  description = "Name of the container (deprecated - use container_definitions)"
  type        = string
  default     = null
}

variable "container_image" {
  description = "Docker image for the container (deprecated - use container_definitions)"
  type        = string
  default     = null
}

variable "container_port" {
  description = "Port exposed by the container (deprecated - use container_definitions)"
  type        = number
  default     = 3000
}

variable "cpu" {
  description = "CPU units for the task"
  type        = string
  default     = "512"
}

variable "memory" {
  description = "Memory for the task (in MiB)"
  type        = string
  default     = "1024"
}

variable "desired_count" {
  description = "Number of task instances to run"
  type        = number
  default     = 1
}

variable "subnet_ids" {
  description = "List of subnet IDs for the service"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for the service"
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Assign public IP to tasks"
  type        = bool
  default     = false
}

variable "execution_role_arn" {
  description = "ARN of the task execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the task role"
  type        = string
}

variable "target_group_arn" {
  description = "ARN of the target group for load balancer"
  type        = string
  default     = null
}

variable "load_balancer_container_name" {
  description = "Name of the container to attach to the load balancer"
  type        = string
  default     = null
}

variable "load_balancer_container_port" {
  description = "Port of the container to attach to the load balancer"
  type        = number
  default     = null
}

# Legacy variables for backward compatibility
variable "port_mappings" {
  description = "Port mappings for the container (deprecated - use container_definitions)"
  type = list(object({
    containerPort = number
    protocol      = string
  }))
  default = []
}

variable "environment_variables" {
  description = "Environment variables for the container (deprecated - use container_definitions)"
  type = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "health_check" {
  description = "Health check configuration (deprecated - use container_definitions)"
  type = object({
    command     = list(string)
    interval    = number
    timeout     = number
    retries     = number
    startPeriod = number
  })
  default = null
}

variable "log_group_name" {
  description = "Name of the CloudWatch log group (deprecated - use container_definitions)"
  type        = string
  default     = null
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "enable_circuit_breaker" {
  description = "Enable deployment circuit breaker"
  type        = bool
  default     = true
}

variable "enable_rollback" {
  description = "Enable automatic rollback on deployment failure"
  type        = bool
  default     = true
}

variable "max_percent" {
  description = "Maximum percentage of tasks to run during deployment"
  type        = number
  default     = 200
}

variable "min_healthy_percent" {
  description = "Minimum percentage of healthy tasks during deployment"
  type        = number
  default     = 100
}

variable "enable_exec" {
  description = "Enable ECS Exec for debugging"
  type        = bool
  default     = false
}

variable "force_new_deployment" {
  description = "Force a new deployment"
  type        = bool
  default     = false
}

variable "service_dependencies" {
  description = "List of resources this service depends on"
  type        = list(any)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
