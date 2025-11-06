variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for interface endpoints"
  type        = list(string)
}

variable "route_table_ids" {
  description = "List of route table IDs for gateway endpoints"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for interface endpoints"
  type        = list(string)
}

variable "enable_ecs_exec" {
  description = "Enable SSM endpoints for ECS Exec"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to endpoints"
  type        = map(string)
  default     = {}
}
