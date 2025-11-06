output "ecr_api_endpoint_id" {
  description = "ID of the ECR API endpoint"
  value       = aws_vpc_endpoint.ecr_api.id
}

output "ecr_dkr_endpoint_id" {
  description = "ID of the ECR DKR endpoint"
  value       = aws_vpc_endpoint.ecr_dkr.id
}

output "s3_endpoint_id" {
  description = "ID of the S3 endpoint"
  value       = aws_vpc_endpoint.s3.id
}

output "logs_endpoint_id" {
  description = "ID of the CloudWatch Logs endpoint"
  value       = aws_vpc_endpoint.logs.id
}
