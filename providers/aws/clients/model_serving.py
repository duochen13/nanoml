import boto3
import json
from typing import Any


class SageMakerServingClient:
    """Amazon SageMaker Endpoint client for model serving."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Serving client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)
        self.runtime = boto3.client("sagemaker-runtime", region_name=region)

    def create_endpoint(
        self,
        endpoint_name: str,
        model_data_s3: str,
        instance_type: str,
        role_arn: str = None
    ) -> str:
        """Create SageMaker endpoint.

        Args:
            endpoint_name: Endpoint name
            model_data_s3: S3 URI to model.tar.gz
            instance_type: Instance type (e.g., ml.t2.medium)
            role_arn: IAM role ARN

        Returns:
            Endpoint name
        """
        model_name = f"{endpoint_name}-model"
        config_name = f"{endpoint_name}-config"

        # Create model
        self.sagemaker.create_model(
            ModelName=model_name,
            PrimaryContainer={
                "Image": f"763104351884.dkr.ecr.{self.region}.amazonaws.com/pytorch-inference:latest",
                "ModelDataUrl": model_data_s3
            },
            ExecutionRoleArn=role_arn or f"arn:aws:iam::123456789012:role/SageMakerRole"
        )

        # Create endpoint config
        self.sagemaker.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    "VariantName": "primary",
                    "ModelName": model_name,
                    "InstanceType": instance_type,
                    "InitialInstanceCount": 1
                }
            ]
        )

        # Create endpoint
        self.sagemaker.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )

        return endpoint_name

    def invoke_endpoint(self, endpoint_name: str, payload: dict) -> Any:
        """Invoke endpoint for prediction.

        Args:
            endpoint_name: Endpoint name
            payload: Input data

        Returns:
            Prediction result
        """
        response = self.runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload)
        )

        # Read response body
        body = response["Body"].read()

        # Handle moto's simple string response
        if isinstance(body, bytes):
            body = body.decode()

        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            # If not JSON, return the raw response
            result = {"prediction": body}

        return result

    def delete_endpoint(self, endpoint_name: str):
        """Delete endpoint.

        Args:
            endpoint_name: Endpoint name
        """
        self.sagemaker.delete_endpoint(EndpointName=endpoint_name)
