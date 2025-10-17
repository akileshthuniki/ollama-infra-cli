variable "project" { type = string }
variable "image_uri" { type = string }
variable "vpc_id" { type = string }
variable "public_subnets" { type = list(string) }
variable "private_subnets" {
	type    = list(string)
	default = []
}
variable "security_groups" { type = list(string) }
variable "cpu" {
	type    = string
	default = "256"
}

variable "memory" {
	type    = string
	default = "1024"
}

variable "desired_count" {
	type    = number
	default = 1
}

variable "region" {
  type = string
}
