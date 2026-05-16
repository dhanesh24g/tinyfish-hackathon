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

# VPC & Networking
variable "vpc_id" {
  description = "VPC ID"
  type        = string
  default     = "vpc-091f33b876ff339d9"
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks and ALB"
  type        = list(string)
  default = [
    "subnet-0cb8a4d72b63dd28e",
    "subnet-044d06ce5793660a6",
    "subnet-0d5bd80f25ef30c7b"
  ]
}

# Security Groups
variable "alb_security_group_id" {
  description = "ALB security group ID"
  type        = string
  default     = "sg-033a13fda198d7111"
}

variable "web_security_group_id" {
  description = "Web security group ID"
  type        = string
  default     = "sg-04fe68e1f819a8681"
}

variable "api_security_group_id" {
  description = "API security group ID"
  type        = string
  default     = "sg-0842e831610d1e05e"
}

# ACM Certificate
variable "acm_certificate_arn" {
  description = "ACM certificate ARN"
  type        = string
  default     = "arn:aws:acm:ap-south-1:059325865474:certificate/0c9c0722-e92c-4b4f-a6d1-4ba2bcb41600"
}

# Image tags
variable "web_image_tag" {
  description = "Web Docker image tag"
  type        = string
  default     = "20260509-1509"
}

variable "api_image_tag" {
  description = "API Docker image tag"
  type        = string
  default     = "20260509-1640"
}
