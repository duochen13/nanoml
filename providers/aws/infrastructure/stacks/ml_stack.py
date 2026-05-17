from aws_cdk import (
    aws_s3 as s3,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    RemovalPolicy
)
from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from .base_stack import BaseStack


class MLStack(BaseStack):
    """ML infrastructure (S3, SageMaker, Feature Store)."""

    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs):
        """Initialize ML stack.

        Args:
            scope: CDK app
            id: Stack ID
            vpc: VPC from networking stack
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # S3 bucket for data
        self.data_bucket = s3.Bucket(
            self,
            "DataBucket",
            bucket_name="nanorec-data",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # S3 bucket for models
        self.model_bucket = s3.Bucket(
            self,
            "ModelBucket",
            bucket_name="nanorec-models",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # IAM role for SageMaker
        self.sagemaker_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Grant S3 access
        self.data_bucket.grant_read_write(self.sagemaker_role)
        self.model_bucket.grant_read_write(self.sagemaker_role)

        # SageMaker Domain
        self.sagemaker_domain = sagemaker.CfnDomain(
            self,
            "SageMakerDomain",
            domain_name="nanorec-domain",
            auth_mode="IAM",
            default_user_settings=sagemaker.CfnDomain.UserSettingsProperty(
                execution_role=self.sagemaker_role.role_arn
            ),
            subnet_ids=[subnet.subnet_id for subnet in vpc.private_subnets],
            vpc_id=vpc.vpc_id
        )
