# Docker Volumes Directory

This directory contains **runtime data** from Docker containers. It is automatically created when you run `make infra-up`.

## What's stored here:

- `postgres/` - PostgreSQL database files
- `redis/` - Redis persistence files
- `kafka/` - Kafka topic data
- `mlflow/` - MLflow experiments and artifacts
- `airflow/` - Airflow DAGs, logs, and plugins
- `zookeeper/` - Zookeeper coordination data
- `flink/` - Flink job state
- `localstack/` - LocalStack S3 data
- `models/` - Trained model files
- `lineage/` - Lineage tracking database

## Important: Do NOT commit this directory!

This directory is in `.gitignore` and should **never be committed** to version control because:

1. **Contains sensitive data** - Database files may include secrets, API keys, or user data
2. **Large file sizes** - Can grow to hundreds of MBs or GBs
3. **Platform-specific** - May not work across different OS or architectures
4. **Regenerated on startup** - Docker creates these automatically

## Clean up

To remove all runtime data and start fresh:

```bash
make infra-down  # Stops containers and removes volumes
```

This will delete all data in this directory and give you a clean slate.
