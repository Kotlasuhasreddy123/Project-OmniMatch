#!/bin/bash
# teardown_aws.sh — Safely delete the OmniMatch CloudFormation stack
# Usage: ./infrastructure/scripts/teardown_aws.sh [dev|staging|prod]
#
# WARNING: This deletes all resources EXCEPT the S3 audit bucket (DeletionPolicy: Retain).
# The audit bucket must be emptied and deleted manually to preserve audit trails.

set -euo pipefail

ENV="${1:-dev}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="omni-match-${ENV}"

echo "WARNING: This will DELETE the CloudFormation stack: ${STACK_NAME}"
echo "The S3 audit log bucket will be RETAINED per HIPAA requirements."
read -p "Type 'DELETE' to confirm: " CONFIRM

if [ "${CONFIRM}" != "DELETE" ]; then
  echo "Aborted."; exit 0
fi

echo "Deleting stack: ${STACK_NAME}..."
aws cloudformation delete-stack \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}"

echo "Waiting for deletion to complete..."
aws cloudformation wait stack-delete-complete \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}"

echo "Stack ${STACK_NAME} deleted."
echo "REMINDER: S3 audit bucket still exists. Delete manually after data retention period."
