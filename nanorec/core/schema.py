"""JSON Schema for NanoRec config.yaml validation."""

CONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["environment", "project"],
    "properties": {
        "environment": {
            "type": "string",
            "enum": ["local", "aws", "gcp", "azure"],
            "description": "Deployment environment"
        },
        "project": {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9-]*$",
                    "description": "Project name (lowercase, hyphens allowed)"
                },
                "version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$",
                    "description": "Semantic version (X.Y.Z)"
                }
            }
        },
        "local": {
            "type": "object",
            "description": "Local environment configuration"
        },
        "aws": {
            "type": "object",
            "description": "AWS environment configuration"
        },
        "gcp": {
            "type": "object",
            "description": "GCP environment configuration"
        },
        "azure": {
            "type": "object",
            "description": "Azure environment configuration"
        },
        "ml": {
            "type": "object",
            "description": "ML-specific configuration",
            "properties": {
                "features": {
                    "type": "object"
                },
                "training": {
                    "type": "object"
                },
                "serving": {
                    "type": "object"
                }
            }
        }
    }
}
