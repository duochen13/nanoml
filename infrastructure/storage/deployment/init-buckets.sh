#!/bin/bash
# Initialize default S3 buckets in LocalStack

set -e

ENDPOINT="http://localhost:4566"

echo "Creating default NanoRec buckets..."

aws --endpoint-url=$ENDPOINT s3 mb s3://nanorec-data || true
aws --endpoint-url=$ENDPOINT s3 mb s3://nanorec-models || true
aws --endpoint-url=$ENDPOINT s3 mb s3://nanorec-artifacts || true

echo "✅ Buckets created"
