resource "aws_lb" "app" {
  name               = "${var.project}-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.public_subnets
  security_groups    = var.security_groups
}

resource "aws_lb_target_group" "tg" {
  name        = "${var.project}-tg-ip"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

# CloudWatch log group for container logs
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project}"
  retention_in_days = 7
}

resource "aws_ecs_cluster" "this" {
  name = "${var.project}-cluster"

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.app.name
      }
    }
  }
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory

  # Execution role is required for Fargate to pull images from ECR and send logs to CloudWatch
  execution_role_arn = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "app"
      image = var.image_uri
      memory = var.memory - 128  # Reserve some memory for system
      memoryReservation = var.memory / 2
      portMappings = [{ containerPort = 8080, hostPort = 8080 }]
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "app"
        }
      }
    }
  ])
}

# IAM role that ECS Fargate uses to pull images and write logs
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project}-ecs-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_service" "service" {
  name            = "${var.project}-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.task.arn
  launch_type     = "FARGATE"
  desired_count   = var.desired_count

  network_configuration {
    subnets         = length(var.private_subnets) > 0 ? var.private_subnets : var.public_subnets
    security_groups = var.security_groups
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = "app"
    container_port   = 8080
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

