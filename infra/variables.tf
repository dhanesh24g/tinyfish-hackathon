variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
  default     = "059325865474"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ai-voice-interviewer"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "web_image_tag" {
  description = "Web Docker image tag"
  type        = string
  default     = "latest"
}

variable "api_image_tag" {
  description = "API Docker image tag"
  type        = string
  default     = "latest"
}