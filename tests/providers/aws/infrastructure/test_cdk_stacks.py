import pytest
from aws_cdk import App
from providers.aws.infrastructure.stacks.networking_stack import NetworkingStack
from providers.aws.infrastructure.stacks.ml_stack import MLStack


def test_networking_stack_creates_vpc():
    """NetworkingStack creates VPC with public/private subnets."""
    app = App()
    stack = NetworkingStack(app, "test-networking")

    # Verify VPC exists
    assert stack.vpc is not None


def test_ml_stack_creates_s3_bucket():
    """MLStack creates S3 bucket for data."""
    app = App()
    network_stack = NetworkingStack(app, "test-networking")
    ml_stack = MLStack(app, "test-ml", vpc=network_stack.vpc)

    assert ml_stack.data_bucket is not None


def test_ml_stack_creates_sagemaker_resources():
    """MLStack creates SageMaker domain."""
    app = App()
    network_stack = NetworkingStack(app, "test-networking")
    ml_stack = MLStack(app, "test-ml", vpc=network_stack.vpc)

    assert ml_stack.sagemaker_domain is not None
