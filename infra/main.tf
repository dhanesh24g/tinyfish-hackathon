terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ─────────────────────────────────────────
# DATA SOURCES — reference existing resources
# ─────────────────────────────────────────

# Existing ECS Cluster
data "aws_ecs_cluster" "main" {
  cluster_name = "ai-interview-agent-cluster"
}

# Existing Task Definitions — always use latest revision
data "aws_ecs_task_definition" "api" {
  task_definition = "ai-voice-interviewer-api"
}

data "aws_ecs_task_definition" "web" {
  task_definition = "ai-voice-interviewer-web"
}

# Existing ACM Certificate
data "aws_acm_certificate" "main" {
  domain   = "interview.dhaneshlabs.com"
  statuses = ["ISSUED"]
}

# ─────────────────────────────────────────
# MODULES
# ─────────────────────────────────────────

module "alb" {
  source = "./modules/alb"

  app_name              = var.app_name
  vpc_id                = var.vpc_id
  subnet_ids            = var.subnet_ids
  alb_security_group_id = var.alb_security_group_id
  acm_certificate_arn   = data.aws_acm_certificate.main.arn
}

module "ecs_services" {
  source = "./modules/ecs_services"

  app_name              = var.app_name
  environment           = var.environment
  aws_account_id        = var.aws_account_id
  aws_region            = var.aws_region
  cluster_id            = data.aws_ecs_cluster.main.id
  api_task_def_arn      = data.aws_ecs_task_definition.api.arn
  web_task_def_arn      = data.aws_ecs_task_definition.web.arn
  api_target_group_arn  = module.alb.api_target_group_arn
  web_target_group_arn  = module.alb.web_target_group_arn
  web_security_group_id = var.web_security_group_id
  api_security_group_id = var.api_security_group_id
  subnet_ids            = var.subnet_ids

  depends_on = [module.alb]
}
