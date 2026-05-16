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
  cluster_name = "${var.app_name}-cluster"
}

# Existing Task Definitions
data "aws_ecs_task_definition" "api" {
  task_definition = "${var.app_name}-api"
}

data "aws_ecs_task_definition" "web" {
  task_definition = "${var.app_name}-web"
}

# Existing ACM Certificate
data "aws_acm_certificate" "main" {
  domain   = "interview.dhaneshlabs.com"
  statuses = ["ISSUED"]
}

# Existing Security Groups
data "aws_security_group" "alb" {
  name = "${var.app_name}-alb-sg"
}

data "aws_security_group" "web" {
  name = "${var.app_name}-web-sg"
}

data "aws_security_group" "api" {
  name = "${var.app_name}-api-sg"
}

# Existing VPC
data "aws_vpc" "main" {
  default = true
}

# Existing Public Subnets
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
}

# ─────────────────────────────────────────
# MODULES
# ─────────────────────────────────────────

module "alb" {
  source = "./modules/alb"

  app_name            = var.app_name
  vpc_id              = data.aws_vpc.main.id
  subnet_ids          = data.aws_subnets.public.ids
  alb_security_group  = data.aws_security_group.alb.id
  acm_certificate_arn = data.aws_acm_certificate.main.arn
}

module "ecs_services" {
  source = "./modules/ecs_services"

  app_name           = var.app_name
  environment        = var.environment
  aws_account_id     = var.aws_account_id
  aws_region         = var.aws_region
  cluster_id         = data.aws_ecs_cluster.main.id
  cluster_name       = data.aws_ecs_cluster.main.cluster_name
  api_task_def_arn   = data.aws_ecs_task_definition.api.arn
  web_task_def_arn   = data.aws_ecs_task_definition.web.arn
  api_target_group   = module.alb.api_target_group_arn
  web_target_group   = module.alb.web_target_group_arn
  web_security_group = data.aws_security_group.web.id
  api_security_group = data.aws_security_group.api.id
  subnet_ids         = data.aws_subnets.public.ids

  depends_on = [module.alb]
}