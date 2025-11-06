# ECS Task Definition
resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.cpu
  memory                  = var.memory
  execution_role_arn      = var.execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode(var.container_definitions)

  tags = var.tags
}

# ECS Service
resource "aws_ecs_service" "this" {
  name            = var.service_name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = var.assign_public_ip
  }

  dynamic "load_balancer" {
    for_each = var.target_group_arn != null ? [1] : []
    content {
      target_group_arn = var.target_group_arn
      container_name   = var.load_balancer_container_name
      container_port   = var.load_balancer_container_port
    }
  }

  deployment_circuit_breaker {
    enable   = var.enable_circuit_breaker
    rollback = var.enable_rollback
  }

  deployment_maximum_percent     = var.max_percent
  deployment_minimum_healthy_percent = var.min_healthy_percent

  deployment_controller {
    type = "ECS"
  }

  enable_execute_command = var.enable_exec

  force_new_deployment = var.force_new_deployment

  tags = var.tags
}
