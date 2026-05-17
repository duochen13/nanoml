from aws_cdk import Stack, Tags
from constructs import Construct


class BaseStack(Stack):
    """Base stack with common configurations."""

    def __init__(self, scope: Construct, id: str, **kwargs):
        """Initialize base stack.

        Args:
            scope: CDK app
            id: Stack ID
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # Common tags
        Tags.of(self).add("Project", "NanoML")
        Tags.of(self).add("ManagedBy", "CDK")
