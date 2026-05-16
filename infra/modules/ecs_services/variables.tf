variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "cluster_id" {
  description = "ECS cluster ID"
  type        = string
}

variable "cluster_name" {
  description = "ECS cluster name"
  type        = string
}

variable "api_task_def_arn" {
  description = "API task definition ARN"
  type        = string
}

variable "web_task_def_arn" {
  description = "Web task definition ARN"
  type        = string
}

variable "api_target_group" {
  description = "API target group ARN"
  type        = string
}

variable "web_target_group" {
  description = "Web target group ARN"
  type        = string
}

variable "web_security_group" {
  description = "Web security group ID"
  type        = string
}

variable "api_security_group" {
  description = "API security group ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks"
  type        = list(string)
}
