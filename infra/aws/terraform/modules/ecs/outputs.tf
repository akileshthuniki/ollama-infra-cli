output "alb_url" {
  value = aws_lb.app.dns_name
}
