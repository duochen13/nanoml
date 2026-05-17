import boto3
from typing import Optional


class SageMakerTrainingClient:
    """Amazon SageMaker Training client."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize Training client."""
        self.region = region
        self.sagemaker = boto3.client("sagemaker", region_name=region)

    def create_training_job(
        self,
        job_name: str,
        algorithm: str,
        instance_type: str,
        input_data_s3: str,
        output_s3: str,
        role_arn: Optional[str] = None,
        hyperparameters: Optional[dict] = None
    ) -> str:
        """Create SageMaker training job.

        Args:
            job_name: Training job name
            algorithm: Algorithm (e.g., xgboost, pytorch)
            instance_type: Instance type (e.g., ml.m5.xlarge)
            input_data_s3: S3 URI for training data
            output_s3: S3 URI for model output
            role_arn: IAM role ARN
            hyperparameters: Training hyperparameters

        Returns:
            Training job name
        """
        # Map algorithm to container image
        algorithm_images = {
            "xgboost": f"433757028032.dkr.ecr.{self.region}.amazonaws.com/xgboost:latest",
            "pytorch": f"763104351884.dkr.ecr.{self.region}.amazonaws.com/pytorch-training:latest"
        }

        config = {
            "TrainingJobName": job_name,
            "RoleArn": role_arn or f"arn:aws:iam::123456789012:role/SageMakerRole",
            "AlgorithmSpecification": {
                "TrainingImage": algorithm_images.get(algorithm),
                "TrainingInputMode": "File"
            },
            "InputDataConfig": [
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": input_data_s3
                        }
                    }
                }
            ],
            "OutputDataConfig": {"S3OutputPath": output_s3},
            "ResourceConfig": {
                "InstanceType": instance_type,
                "InstanceCount": 1,
                "VolumeSizeInGB": 30
            },
            "StoppingCondition": {"MaxRuntimeInSeconds": 3600}
        }

        if hyperparameters:
            config["HyperParameters"] = hyperparameters

        self.sagemaker.create_training_job(**config)

        return job_name

    def wait_for_training_job(self, job_name: str):
        """Wait for training job to complete.

        Args:
            job_name: Training job name
        """
        waiter = self.sagemaker.get_waiter("training_job_completed_or_stopped")
        waiter.wait(TrainingJobName=job_name)

    def get_training_job_status(self, job_name: str) -> str:
        """Get training job status.

        Args:
            job_name: Training job name

        Returns:
            Status (InProgress, Completed, Failed, etc.)
        """
        response = self.sagemaker.describe_training_job(TrainingJobName=job_name)
        return response["TrainingJobStatus"]
