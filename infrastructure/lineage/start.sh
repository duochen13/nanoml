#!/bin/bash
# Start the lineage API server

cd "$(dirname "$0")"
uvicorn api:app --host 0.0.0.0 --port 9000 --reload
