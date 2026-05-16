# ─────────────────────────────────────────
# ECS SERVICE — API
# ─────────────────────────────────────────

resource "aws_ecs_service" "api" {
  name            = "${var.app_name}-api-service"
  cluster         = var.cluster_id
  task_definition = var.api_task_def_arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.api_security_group]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.api_target_group
    container_name   = "api"
    container_port   = 8000
  }

  lifecycle {
    ignore_changes = [
      # Ignore task definition changes
      # so CI/CD can update without Terraform overriding
      task_definition,
      desired_count
    ]
  }

  tags = {
    Name        = "${var.app_name}-api-service"
    Environment = var.environment
  }
}

# ─────────────────────────────────────────
# ECS SERVICE — WEB
# ─────────────────────────────────────────

resource "aws_ecs_service" "web" {
  name            = "${var.app_name}-web-service"
  cluster         = var.cluster_id
  task_definition = var.web_task_def_arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.web_security_group]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.web_target_group
    container_name   = "web"
    container_port   = 3000
  }

  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }

  tags = {
    Name        = "${var.app_name}-web-service"
    Environment = var.environment
  }
}
