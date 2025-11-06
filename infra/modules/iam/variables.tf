variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "log_group_arns" {
  description = "ARNs of CloudWatch log groups"
  type        = list(string)
  default     = ["*"]
}

variable "enable_ecs_exec" {
  description = "Enable ECS Exec permissions"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to IAM roles"
  type        = map(string)
  default     = {}
}
