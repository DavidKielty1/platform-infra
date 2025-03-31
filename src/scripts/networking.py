from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_kms as kms,
    RemovalPolicy,
    Stack,
    CfnOutput,
    Tags
)
from constructs import Construct
from scripts.config import PlatformConfig

class NetworkingConstruct(Construct):
    """Networking infrastructure for the platform."""
    
    def __init__(self, scope: Construct, config: PlatformConfig) -> None:
        super().__init__(scope, "NetworkingConstruct")
        
        self.config = config
        
        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            "PlatformVPC",
            vpc_name="platform-vpc",
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

        # Create security group for application
        self.security_group = ec2.SecurityGroup(
            self,
            "ApplicationSecurityGroup",
            vpc=self.vpc,
            description="Security group for application resources",
            allow_all_outbound=True
        )

        # Add inbound rule for application port
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(5000),
            description="Allow inbound HTTP traffic"
        )

        # Add tags to resources
        Tags.of(self.vpc).add("Name", "platform-vpc")
        Tags.of(self.security_group).add("Name", f"{config.project}-app-sg")

        # Output values
        CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
        CfnOutput(self, "SecurityGroupId", value=self.security_group.security_group_id) 