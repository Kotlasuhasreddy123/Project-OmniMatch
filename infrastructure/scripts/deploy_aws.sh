#!/bin/bash
# deploy_aws.sh — Deploy OmniMatch to AWS using CloudFormation
# Usage: ./infrastructure/scripts/deploy_aws.sh [dev|staging|prod]
#
# Prerequisites:
#   1. aws cli v2 configured: aws configure
#   2. EC2 Key Pair created in your target region
#   3. Docker installed locally for image build/push (optional)
#
# HIPAA NOTE: This is a SIMULATED academic deployment. For real PHI workloads,
# sign the AWS Business Associate Addendum (BAA) via AWS Artifact first.

set -euo pipefail

ENV="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="omni-match-${ENV}"
TEMPLATE="infrastructure/aws/cloudformation.yml"

echo "╔══════════════════════════════════════════════╗"
echo "║   OmniMatch AWS Deployment — ${ENV}          ║"
echo "╚══════════════════════════════════════════════╝"
echo "Region: ${REGION}"
echo "Stack:  ${STACK_NAME}"
echo ""

# ── Prompt for secrets (never hardcoded) ──────────────────────────────────
read -s -p "JWT Secret Key (32+ chars): " JWT_SECRET; echo
read -s -p "App Secret Key (32+ chars): " APP_SECRET; echo
read    -p "EC2 Key Pair Name: " KEY_PAIR
read    -p "Your IP CIDR for SSH (e.g. 1.2.3.4/32): " ALLOWED_CIDR

if [ ${#JWT_SECRET} -lt 32 ]; then
  echo "ERROR: JWT_SECRET must be at least 32 characters"; exit 1
fi

# ── Deploy or update CloudFormation stack ─────────────────────────────────
echo ""
echo "Deploying CloudFormation stack..."

aws cloudformation deploy \
  --template-file "${TEMPLATE}" \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    EnvironmentName="omni-${ENV}" \
    KeyPairName="${KEY_PAIR}" \
    AllowedCIDR="${ALLOWED_CIDR}" \
    JWTSecret="${JWT_SECRET}" \
    AppSecretKey="${APP_SECRET}" \
  --tags \
    Project=OmniMatch \
    Environment="${ENV}" \
    ManagedBy=CloudFormation

# ── Get outputs ───────────────────────────────────────────────────────────
echo ""
echo "Stack deployed. Fetching outputs..."

EC2_IP=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='EC2PublicIP'].OutputValue" \
  --output text)

ALB_DNS=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='ALBDNSName'].OutputValue" \
  --output text)

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Deployment Complete!                       ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  EC2 IP:    ${EC2_IP}"
echo "║  ALB DNS:   ${ALB_DNS}"
echo "║  Backend:   http://${EC2_IP}:8000/api/docs"
echo "║  Frontend:  http://${EC2_IP}:3000"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Point your domain DNS to: ${ALB_DNS}"
echo "  2. Add an ACM certificate to the ALB HTTPS listener"
echo "  3. SSH: ssh -i ~/.ssh/${KEY_PAIR}.pem ec2-user@${EC2_IP}"
echo "  4. Seed trials: ssh ec2-user@${EC2_IP} 'cd app && docker compose exec backend python scripts/seed_trials.py --max 100'"
