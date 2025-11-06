variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "image_tag_mutability" {
  description = "Image tag mutability setting for the repository"
  type        = string
}

variable "image_retention_count" {
  description = "Number of images to keep in the repository"
  type        = number
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
}