#!/bin/bash

# ─────────────────────────────────────────
# Starts ECS services (sets desired count to 1)
# ─────────────────────────────────────────

set -euo pipefail

CLUSTER="ai-interview-agent-cluster"
REGION="ap-south-1"

echo "Starting ECS services..."

aws ecs update-service \
  --cluster $CLUSTER \
  --service ai-voice-interviewer-api-service-qlczxivk \
  --desired-count 1 \
  --region $REGION > /dev/null

aws ecs update-service \
  --cluster $CLUSTER \
  --service ai-voice-interviewer-web-service-tesg8voh \
  --desired-count 1 \
  --region $REGION > /dev/null

echo "Services started!"
echo "Wait 2-3 mins for tasks to reach RUNNING state"
echo "App: https://interview.dhaneshlabs.com"
