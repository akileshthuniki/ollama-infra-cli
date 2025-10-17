variable "project" {
  type = string
}

variable "region" {
  type = string
  default = "us-east-1"
}

variable "image_uri" {
  type = string
}

variable "vpc_id" { type = string }
variable "public_subnets" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "security_groups" { type = list(string) }
