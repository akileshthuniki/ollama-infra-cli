provider "aws" {
  region = var.region
}

module "ecr" {
  source = "../modules/ecr"
  name   = var.project
}

module "ecs" {
  source = "../modules/ecs"
  project = var.project
  image_uri = var.image_uri
  vpc_id = var.vpc_id
  public_subnets = var.public_subnets
  private_subnets = var.private_subnets
  security_groups = var.security_groups
  region = var.region
}

