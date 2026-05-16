output "api_service_name" {
  description = "API ECS service name"
  value       = aws_ecs_service.api.name
}

output "web_service_name" {
  description = "Web ECS service name"
  value       = aws_ecs_service.web.name
}

output "api_service_id" {
  description = "API ECS service ID"
  value       = aws_ecs_service.api.id
}

output "web_service_id" {
  description = "Web ECS service ID"
  value       = aws_ecs_service.web.id
}
