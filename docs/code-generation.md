# Code Generation in NanoRec

NanoRec automatically generates infrastructure code from your high-level definitions. This document explains what gets generated and how.

## Overview

When you run `nanorec generate`, NanoRec reads your user code and generates:

1. **Flink Streaming Jobs** - From `features/definitions.py`
2. **Feast Configuration** - From `features/definitions.py`
3. **Airflow DAGs** - From `components/*.py`

All generated code is written to `.nanorec/generated/` and should not be edited manually.

## Directory Structure

```
.nanorec/generated/
├── flink/
│   └── streaming_features.py    # Flink job for feature computation
├── feast/
│   ├── feature_store.yaml        # Feast configuration
│   └── features.py               # Entity and FeatureView definitions
└── airflow/
    └── pipeline_dag.py           # Orchestration DAG
```

## Flink Job Generation

**Input:** `features/definitions.py`

**Output:** `.nanorec/generated/flink/streaming_features.py`

The generator:
1. Parses `FeatureGroup` definitions using AST
2. Creates a Kafka consumer per feature group
3. Generates feature extraction logic
4. Writes results to Feast via Kafka topics

**Example:**

```python
# features/definitions.py
user_features = FeatureGroup(
    name="user_features",
    entity="user_id",
    features=[Feature("age", "int")],
    source="kafka://user_events"
)
```

Generates a Flink job that:
- Consumes from `user_events` Kafka topic
- Extracts `age` field and `user_id` entity
- Publishes to `feast_user_features` Kafka topic

## Feast Configuration Generation

**Input:** `features/definitions.py`

**Outputs:**
- `.nanorec/generated/feast/feature_store.yaml`
- `.nanorec/generated/feast/features.py`

The generator:
1. Extracts unique entities from all `FeatureGroup` definitions
2. Creates Feast `Entity` definitions
3. Creates Feast `FeatureView` definitions with schema

**Example:**

```python
# Generated features.py
user_id = Entity(
    name="user_id",
    description="Auto-generated entity for user_id"
)

user_features = FeatureView(
    name="user_features",
    entities=[user_id],
    schema=[
        Field(name="age", dtype=Int64)
    ],
    ...
)
```

## Airflow DAG Generation

**Input:** `components/*.py`

**Output:** `.nanorec/generated/airflow/pipeline_dag.py`

The generator:
1. Parses component definitions (DataComponent, FeaturesComponent, etc.)
2. Creates PythonOperator per component
3. Sets task dependencies from `depends_on` field

**Example:**

```python
# components/pipeline.py
data = DataComponent(name="ingest")
features = FeaturesComponent(name="compute", depends_on=[data])
```

Generates:
```python
ingest >> compute
```

## Usage

### Generate All Code

```bash
nanorec generate
```

### Clean and Regenerate

```bash
nanorec generate --clean
```

This removes all existing generated code before regenerating.

## When to Regenerate

Run `nanorec generate` whenever you:
- Add/modify feature definitions
- Add/modify components
- Change dependencies between components

## Generated Code Guarantees

1. **Idempotent** - Running generate multiple times produces identical output
2. **Complete** - All information from user definitions is preserved
3. **Valid** - Generated code passes syntax checks (compile for Python, parse for YAML)
4. **Deterministic** - Same input always produces same output

## Debugging Generated Code

If generated code doesn't work:

1. Check the source definitions for errors
2. Run `nanorec validate` to catch config issues
3. Examine generated files in `.nanorec/generated/`
4. File an issue if generation is incorrect

Generated code includes comments showing:
- Source file it was generated from
- Warning not to edit manually
- Regeneration command

## Customization

Generated code is intentionally not customizable. If you need different behavior:

1. Modify your source definitions
2. File a feature request for new generation patterns
3. For one-off needs, implement manually in `components/` instead of relying on generation
