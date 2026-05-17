#!/bin/bash
# Initialize default S3 buckets in LocalStack

set -e

ENDPOINT="http://localhost:4566"

echo "Creating default NanoML buckets..."

aws --endpoint-url=$ENDPOINT s3 mb s3://nanoml-data || true
aws --endpoint-url=$ENDPOINT s3 mb s3://nanoml-models || true
aws --endpoint-url=$ENDPOINT s3 mb s3://nanoml-artifacts || true

echo "✅ Buckets created"
