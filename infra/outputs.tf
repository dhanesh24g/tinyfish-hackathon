output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "app_url" {
  description = "Application URL"
  value       = "https://interview.dhaneshlabs.com"
}

output "api_url" {
  description = "API URL"
  value       = "https://interview.dhaneshlabs.com/api"
}
