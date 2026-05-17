#!/bin/bash
# Start the lineage API server

cd "$(dirname "$0")/../.."
python3 -m uvicorn infrastructure.lineage.api:app --host 0.0.0.0 --port 9000 --reload
