#!/bin/bash

# ─────────────────────────────────────────
# Captures current AWS infrastructure state
# Output saved to infra/backups/
# ─────────────────────────────────────────

set -euo pipefail

ALB_ARN="arn:aws:elasticloadbalancing:ap-south-1:059325865474:loadbalancer/app/ai-voice-interviewer-alb/835cc7770a06cbad"
CLUSTER="ai-interview-agent-cluster"
REGION="ap-south-1"
OUTPUT_FILE="infra/backups/aws-backup-$(date +%Y%m%d-%H%M).json"

echo "Capturing AWS infrastructure state..."
echo "Output: $OUTPUT_FILE"

# Get listener ARNs
HTTP_LISTENER=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --region $REGION \
  --query 'Listeners[?Port==`80`].ListenerArn' \
  --output text)

HTTPS_LISTENER=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --region $REGION \
  --query 'Listeners[?Port==`443`].ListenerArn' \
  --output text)

# Build JSON output
jq -n \
  --argjson alb "$(aws elbv2 describe-load-balancers --names ai-voice-interviewer-alb --region $REGION)" \
  --argjson listeners "$(aws elbv2 describe-listeners --load-balancer-arn $ALB_ARN --region $REGION)" \
  --argjson target_groups "$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN --region $REGION)" \
  --argjson http_rules "$(aws elbv2 describe-rules --listener-arn $HTTP_LISTENER --region $REGION)" \
  --argjson https_rules "$(aws elbv2 describe-rules --listener-arn $HTTPS_LISTENER --region $REGION)" \
  --argjson security_groups "$(aws ec2 describe-security-groups --filters 'Name=group-name,Values=ai-voice-interviewer-*' --region $REGION)" \
  --argjson ecs_cluster "$(aws ecs describe-clusters --clusters $CLUSTER --region $REGION)" \
  --argjson ecs_services "$(aws ecs describe-services --cluster $CLUSTER --services ai-voice-interviewer-api-service-qlczxivk ai-voice-interviewer-web-service-tesg8voh --region $REGION)" \
  --argjson task_def_api "$(aws ecs describe-task-definition --task-definition ai-voice-interviewer-api --region $REGION)" \
  --argjson task_def_web "$(aws ecs describe-task-definition --task-definition ai-voice-interviewer-web --region $REGION)" \
  --argjson ecr_api "$(aws ecr list-images --repository-name ai-interview-agent-api --region $REGION)" \
  --argjson ecr_web "$(aws ecr list-images --repository-name ai-interview-agent-web --region $REGION)" \
  --argjson secrets "$(aws secretsmanager list-secrets --region $REGION)" \
  --argjson acm "$(aws acm list-certificates --region $REGION)" \
  --argjson vpc "$(aws ec2 describe-vpcs --filters 'Name=isDefault,Values=true' --region $REGION)" \
  --argjson subnets "$(aws ec2 describe-subnets --filters 'Name=defaultForAz,Values=true' --region $REGION)" \
  '{
    alb: $alb,
    listeners: $listeners,
    target_groups: $target_groups,
    http_rules: $http_rules,
    https_rules: $https_rules,
    security_groups: $security_groups,
    ecs_cluster: $ecs_cluster,
    ecs_services: $ecs_services,
    task_def_api: $task_def_api,
    task_def_web: $task_def_web,
    ecr_api: $ecr_api,
    ecr_web: $ecr_web,
    secrets: $secrets,
    acm: $acm,
    vpc: $vpc,
    subnets: $subnets
  }' > $OUTPUT_FILE

echo "Done! Saved to: $OUTPUT_FILE"
