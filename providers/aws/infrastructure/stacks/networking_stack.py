from aws_cdk import aws_ec2 as ec2
from constructs import Construct
from .base_stack import BaseStack


class NetworkingStack(BaseStack):
    """Networking infrastructure (VPC, subnets, security groups)."""

    def __init__(self, scope: Construct, id: str, cidr: str = "10.0.0.0/16", **kwargs):
        """Initialize networking stack.

        Args:
            scope: CDK app
            id: Stack ID
            cidr: VPC CIDR block
            **kwargs: Additional stack parameters
        """
        super().__init__(scope, id, **kwargs)

        # VPC with public and private subnets
        self.vpc = ec2.Vpc(
            self,
            "NanoMLVPC",
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # Security group for SageMaker
        self.sagemaker_sg = ec2.SecurityGroup(
            self,
            "SageMakerSecurityGroup",
            vpc=self.vpc,
            description="Security group for SageMaker resources"
        )

        # Security group for MSK
        self.msk_sg = ec2.SecurityGroup(
            self,
            "MSKSecurityGroup",
            vpc=self.vpc,
            description="Security group for MSK cluster"
        )

        self.msk_sg.add_ingress_rule(
            peer=self.msk_sg,
            connection=ec2.Port.tcp(9092),
            description="Kafka broker communication"
        )
