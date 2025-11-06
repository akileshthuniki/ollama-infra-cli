# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.name}"
  retention_in_days = var.log_retention_days
    tags = merge(var.tags, {
        Name = "${var.name}-logs"
    })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.name}-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.cpu_threshold
  alarm_description   = "CPU utilization high"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = var.service_name
  }

  tags = merge(var.tags, {
    Name = "${var.name}-cpu-alarm"
  })
}

resource "aws_cloudwatch_metric_alarm" "memory_high" {
  alarm_name          = "${var.name}-memory-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = var.memory_threshold
  alarm_description   = "Memory utilization high"
  alarm_actions       = var.alarm_actions

  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = var.service_name
  }

  tags = merge(var.tags, {
    Name = "${var.name}-memory-alarm"
  })
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "ecs" {
  dashboard_name = "${var.name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", var.service_name, "ClusterName", var.cluster_name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "ECS Service Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "RunningTaskCount", "ServiceName", var.service_name, "ClusterName", var.cluster_name]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "Running Tasks"
          period  = 300
        }
      }
    ]
  })
}