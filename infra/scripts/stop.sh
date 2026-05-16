#!/bin/bash

# ─────────────────────────────────────────
# Stops ECS services (sets desired count to 0)
# ─────────────────────────────────────────

set -euo pipefail

CLUSTER="ai-interview-agent-cluster"
REGION="ap-south-1"

echo "Stopping ECS services..."

aws ecs update-service \
  --cluster $CLUSTER \
  --service ai-voice-interviewer-api-service-qlczxivk \
  --desired-count 0 \
  --region $REGION > /dev/null

aws ecs update-service \
  --cluster $CLUSTER \
  --service ai-voice-interviewer-web-service-tesg8voh \
  --desired-count 0 \
  --region $REGION > /dev/null

echo "✅ Services stopped!"
