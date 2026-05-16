# ─────────────────────────────────────────
# ECS SERVICE — API
# ─────────────────────────────────────────

resource "aws_ecs_service" "api" {
  name            = "${var.app_name}-api-service"
  cluster         = var.cluster_id
  task_definition = var.api_task_def_arn
  desired_count   = 1

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.api_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.api_target_group_arn
    container_name   = "api"
    container_port   = 8000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  health_check_grace_period_seconds  = 0
  scheduling_strategy                = "REPLICA"
  enable_ecs_managed_tags            = true

  lifecycle {
    ignore_changes = [
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

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [var.web_security_group_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = var.web_target_group_arn
    container_name   = "web"
    container_port   = 3000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  health_check_grace_period_seconds  = 0
  scheduling_strategy                = "REPLICA"
  enable_ecs_managed_tags            = true

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
