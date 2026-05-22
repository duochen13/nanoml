"""Workflow Designer Constants - Single Source of Truth

All node types, categories, and configuration schemas for the workflow designer.
Frontend fetches these via API - no hardcoded types in React.
"""

# Node Categories
NODE_CATEGORIES = [
    {"id": "data_sources", "label": "Data Sources", "color": "#3b82f6"},
    {"id": "processing", "label": "Processing", "color": "#8b5cf6"},
    {"id": "streaming", "label": "Streaming", "color": "#06b6d4"},
    {"id": "storage", "label": "Storage", "color": "#10b981"},
    {"id": "ml", "label": "ML/Training", "color": "#f59e0b"},
    {"id": "serving", "label": "Serving", "color": "#ef4444"},
]

# Node Type Definitions
NODE_TYPES = {
    # Data Sources
    "raw_dataset": {
        "id": "raw_dataset",
        "category": "data_sources",
        "label": "Raw Dataset",
        "icon": "📊",
        "description": "Raw data source (CSV, Parquet, JSON)",
        "config_schema": {
            "source": {
                "type": "string",
                "label": "Data Source",
                "required": True,
                "placeholder": "s3://bucket/data.csv"
            },
            "format": {
                "type": "select",
                "label": "Format",
                "options": ["csv", "parquet", "json", "avro"],
                "default": "csv"
            }
        },
        "max_inputs": 0,
        "max_outputs": -1  # unlimited
    },

    "api_source": {
        "id": "api_source",
        "category": "data_sources",
        "label": "API Source",
        "icon": "🔌",
        "description": "External API data source",
        "config_schema": {
            "endpoint": {
                "type": "string",
                "label": "API Endpoint",
                "required": True,
                "placeholder": "https://api.example.com/data"
            },
            "method": {
                "type": "select",
                "label": "HTTP Method",
                "options": ["GET", "POST"],
                "default": "GET"
            },
            "auth_type": {
                "type": "select",
                "label": "Authentication",
                "options": ["none", "bearer", "api_key", "oauth2"],
                "default": "none"
            }
        },
        "max_inputs": 0,
        "max_outputs": -1
    },

    # Processing
    "data_transformation": {
        "id": "data_transformation",
        "category": "processing",
        "label": "Data Transformation",
        "icon": "⚙️",
        "description": "Transform and clean data",
        "config_schema": {
            "transformation_type": {
                "type": "select",
                "label": "Transformation",
                "options": ["filter", "aggregate", "join", "pivot", "custom"],
                "default": "filter"
            },
            "code": {
                "type": "text",
                "label": "Transformation Code",
                "placeholder": "df.filter(col('age') > 18)"
            }
        },
        "max_inputs": -1,
        "max_outputs": -1
    },

    "feature_engineering": {
        "id": "feature_engineering",
        "category": "processing",
        "label": "Feature Engineering",
        "icon": "🔧",
        "description": "Engineer features for ML",
        "config_schema": {
            "features": {
                "type": "text",
                "label": "Feature Definitions",
                "placeholder": "user_avg_rating, rating_std, rating_count"
            },
            "window": {
                "type": "string",
                "label": "Time Window",
                "placeholder": "7d"
            }
        },
        "max_inputs": -1,
        "max_outputs": -1
    },

    # Streaming
    "kafka_source": {
        "id": "kafka_source",
        "category": "streaming",
        "label": "Kafka Source",
        "icon": "📡",
        "description": "Kafka stream consumer",
        "config_schema": {
            "topic": {
                "type": "string",
                "label": "Topic",
                "required": True,
                "placeholder": "user-events"
            },
            "bootstrap_servers": {
                "type": "string",
                "label": "Bootstrap Servers",
                "default": "localhost:9092"
            },
            "consumer_group": {
                "type": "string",
                "label": "Consumer Group",
                "placeholder": "feature-processor"
            }
        },
        "max_inputs": 0,
        "max_outputs": -1
    },

    "flink_job": {
        "id": "flink_job",
        "category": "streaming",
        "label": "Flink Job",
        "icon": "🌊",
        "description": "Flink streaming job",
        "config_schema": {
            "job_name": {
                "type": "string",
                "label": "Job Name",
                "required": True
            },
            "parallelism": {
                "type": "number",
                "label": "Parallelism",
                "default": 1
            },
            "checkpoint_interval": {
                "type": "string",
                "label": "Checkpoint Interval",
                "default": "60s"
            }
        },
        "max_inputs": -1,
        "max_outputs": -1
    },

    # Storage
    "feature_store": {
        "id": "feature_store",
        "category": "storage",
        "label": "Feature Store",
        "icon": "🗄️",
        "description": "Feast feature store",
        "config_schema": {
            "feature_view": {
                "type": "string",
                "label": "Feature View",
                "required": True,
                "placeholder": "user_features"
            },
            "entities": {
                "type": "string",
                "label": "Entities",
                "placeholder": "user_id"
            },
            "ttl": {
                "type": "string",
                "label": "TTL",
                "default": "365d"
            }
        },
        "max_inputs": -1,
        "max_outputs": -1
    },

    "data_warehouse": {
        "id": "data_warehouse",
        "category": "storage",
        "label": "Data Warehouse",
        "icon": "🏢",
        "description": "Data warehouse sink/source",
        "config_schema": {
            "table": {
                "type": "string",
                "label": "Table",
                "required": True
            },
            "warehouse_type": {
                "type": "select",
                "label": "Type",
                "options": ["snowflake", "bigquery", "redshift", "postgres"],
                "default": "postgres"
            }
        },
        "max_inputs": -1,
        "max_outputs": -1
    },

    # ML/Training
    "model_training": {
        "id": "model_training",
        "category": "ml",
        "label": "Model Training",
        "icon": "🎯",
        "description": "Train ML model",
        "config_schema": {
            "algorithm": {
                "type": "select",
                "label": "Algorithm",
                "options": ["random_forest", "xgboost", "neural_network", "linear_regression"],
                "default": "random_forest"
            },
            "hyperparameters": {
                "type": "text",
                "label": "Hyperparameters (JSON)",
                "placeholder": '{"n_estimators": 100, "max_depth": 5}'
            },
            "target": {
                "type": "string",
                "label": "Target Column",
                "required": True
            }
        },
        "max_inputs": -1,
        "max_outputs": 1
    },

    "model_evaluation": {
        "id": "model_evaluation",
        "category": "ml",
        "label": "Model Evaluation",
        "icon": "📈",
        "description": "Evaluate model performance",
        "config_schema": {
            "metrics": {
                "type": "select",
                "label": "Metrics",
                "options": ["rmse", "mae", "accuracy", "precision", "recall", "f1"],
                "multiple": True
            },
            "test_size": {
                "type": "number",
                "label": "Test Size",
                "default": 0.2
            }
        },
        "max_inputs": 2,  # model + test data
        "max_outputs": 1
    },

    # Serving
    "model_registry": {
        "id": "model_registry",
        "category": "serving",
        "label": "Model Registry",
        "icon": "📦",
        "description": "MLflow model registry",
        "config_schema": {
            "model_name": {
                "type": "string",
                "label": "Model Name",
                "required": True
            },
            "stage": {
                "type": "select",
                "label": "Stage",
                "options": ["staging", "production", "archived"],
                "default": "staging"
            }
        },
        "max_inputs": 1,
        "max_outputs": -1
    },

    "model_serving": {
        "id": "model_serving",
        "category": "serving",
        "label": "Model Serving",
        "icon": "🚀",
        "description": "Deploy model for inference",
        "config_schema": {
            "endpoint": {
                "type": "string",
                "label": "Endpoint Path",
                "placeholder": "/predict"
            },
            "batch_size": {
                "type": "number",
                "label": "Batch Size",
                "default": 32
            },
            "timeout_ms": {
                "type": "number",
                "label": "Timeout (ms)",
                "default": 5000
            }
        },
        "max_inputs": 2,  # model + feature source
        "max_outputs": 0
    },
}

# Workflow Statuses
WORKFLOW_STATUSES = [
    {"id": "draft", "label": "Draft", "color": "#gray"},
    {"id": "active", "label": "Active", "color": "#10b981"},
    {"id": "archived", "label": "Archived", "color": "#6b7280"},
]

# Pipeline Types
PIPELINE_TYPES = [
    {"id": "batch", "label": "Batch Training"},
    {"id": "streaming", "label": "Real-time Streaming"},
    {"id": "inference", "label": "Inference"},
    {"id": "feature", "label": "Feature Engineering"},
]


def get_config():
    """Get complete workflow configuration for frontend"""
    return {
        "node_categories": NODE_CATEGORIES,
        "node_types": NODE_TYPES,
        "workflow_statuses": WORKFLOW_STATUSES,
        "pipeline_types": PIPELINE_TYPES,
    }
