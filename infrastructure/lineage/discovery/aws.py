"""AWS resource discovery service."""

import os
from typing import List, Optional
from .base import BaseDiscovery, DiscoveredComponent, ComponentCategory

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class AWSDiscovery(BaseDiscovery):
    """Discover ML components from AWS services."""

    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """Initialize AWS discovery.

        Args:
            region: AWS region (defaults to AWS_DEFAULT_REGION env var or us-east-1)
            profile: AWS profile name (optional)
        """
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.profile = profile
        self._session: Optional[boto3.Session] = None

    def is_available(self) -> bool:
        """Check if AWS credentials are configured."""
        if not BOTO3_AVAILABLE:
            return False

        try:
            session = self._get_session()
            # Try a simple STS call to verify credentials
            sts = session.client("sts")
            sts.get_caller_identity()
            return True
        except (ClientError, NoCredentialsError):
            return False

    def _get_session(self) -> boto3.Session:
        """Get or create boto3 session."""
        if self._session is None:
            if self.profile:
                self._session = boto3.Session(profile_name=self.profile, region_name=self.region)
            else:
                self._session = boto3.Session(region_name=self.region)
        return self._session

    async def discover(self) -> List[DiscoveredComponent]:
        """Discover AWS resources.

        Returns:
            List of discovered AWS components
        """
        if not self.is_available():
            return []

        components = []

        try:
            session = self._get_session()

            # Discover S3 buckets
            components.extend(await self._discover_s3(session))

            # Discover SageMaker endpoints
            components.extend(await self._discover_sagemaker(session))

            # Discover EMR clusters
            components.extend(await self._discover_emr(session))

            # Discover Lambda functions
            components.extend(await self._discover_lambda(session))

        except Exception as e:
            print(f"Error discovering AWS resources: {e}")

        return components

    async def _discover_s3(self, session: boto3.Session) -> List[DiscoveredComponent]:
        """Discover S3 buckets."""
        components = []

        try:
            s3 = session.client("s3")
            response = s3.list_buckets()

            for bucket in response.get("Buckets", []):
                bucket_name = bucket["Name"]

                # Try to get bucket region
                try:
                    location = s3.get_bucket_location(Bucket=bucket_name)
                    bucket_region = location["LocationConstraint"] or "us-east-1"
                except:
                    bucket_region = self.region

                # Check if bucket name suggests ML data
                is_ml_related = any(keyword in bucket_name.lower()
                                   for keyword in ["data", "ml", "model", "train", "feature"])

                if is_ml_related:
                    components.append(DiscoveredComponent(
                        id=f"s3_{bucket_name}",
                        name=bucket_name,
                        type="s3_bucket",
                        provider="aws",
                        category=ComponentCategory.DATA_SOURCES,
                        metadata={
                            "region": bucket_region,
                            "arn": f"arn:aws:s3:::{bucket_name}",
                            "created_at": bucket["CreationDate"].isoformat(),
                        }
                    ))

        except Exception as e:
            print(f"Error discovering S3 buckets: {e}")

        return components

    async def _discover_sagemaker(self, session: boto3.Session) -> List[DiscoveredComponent]:
        """Discover SageMaker endpoints."""
        components = []

        try:
            sagemaker = session.client("sagemaker")
            response = sagemaker.list_endpoints(MaxResults=100)

            for endpoint in response.get("Endpoints", []):
                endpoint_name = endpoint["EndpointName"]

                # Get endpoint details
                try:
                    details = sagemaker.describe_endpoint(EndpointName=endpoint_name)

                    components.append(DiscoveredComponent(
                        id=f"sagemaker_{endpoint_name}",
                        name=endpoint_name,
                        type="sagemaker_endpoint",
                        provider="aws",
                        category=ComponentCategory.SERVING,
                        metadata={
                            "status": endpoint["EndpointStatus"],
                            "arn": endpoint["EndpointArn"],
                            "created_at": endpoint["CreationTime"].isoformat(),
                            "instance_type": details.get("ProductionVariants", [{}])[0].get("InstanceType"),
                        }
                    ))
                except:
                    pass

        except Exception as e:
            print(f"Error discovering SageMaker endpoints: {e}")

        return components

    async def _discover_emr(self, session: boto3.Session) -> List[DiscoveredComponent]:
        """Discover EMR (Spark) clusters."""
        components = []

        try:
            emr = session.client("emr")
            response = emr.list_clusters(ClusterStates=["STARTING", "RUNNING", "WAITING"])

            for cluster in response.get("Clusters", []):
                cluster_id = cluster["Id"]
                cluster_name = cluster["Name"]

                components.append(DiscoveredComponent(
                    id=f"emr_{cluster_id}",
                    name=cluster_name,
                    type="emr_cluster",
                    provider="aws",
                    category=ComponentCategory.PROCESSING,
                    metadata={
                        "cluster_id": cluster_id,
                        "status": cluster["Status"]["State"],
                        "created_at": cluster["Status"]["Timeline"]["CreationDateTime"].isoformat(),
                    }
                ))

        except Exception as e:
            print(f"Error discovering EMR clusters: {e}")

        return components

    async def _discover_lambda(self, session: boto3.Session) -> List[DiscoveredComponent]:
        """Discover Lambda functions (data processing)."""
        components = []

        try:
            lambda_client = session.client("lambda")
            response = lambda_client.list_functions(MaxItems=100)

            for function in response.get("Functions", []):
                function_name = function["FunctionName"]

                # Check if Lambda is ML-related
                is_ml_related = any(keyword in function_name.lower()
                                   for keyword in ["data", "ml", "model", "preprocess", "feature"])

                if is_ml_related:
                    components.append(DiscoveredComponent(
                        id=f"lambda_{function_name}",
                        name=function_name,
                        type="lambda_function",
                        provider="aws",
                        category=ComponentCategory.PROCESSING,
                        metadata={
                            "arn": function["FunctionArn"],
                            "runtime": function["Runtime"],
                            "memory_mb": function["MemorySize"],
                            "timeout_sec": function["Timeout"],
                        }
                    ))

        except Exception as e:
            print(f"Error discovering Lambda functions: {e}")

        return components
