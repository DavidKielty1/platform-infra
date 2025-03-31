#!/usr/bin/env python3
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aws_cdk import App, Environment, Stack, CfnOutput
from scripts.networking import NetworkingConstruct
from scripts.container import ContainerConstruct
from scripts.config import PlatformConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NetworkingStack(Stack):
    """Networking infrastructure stack."""
    
    def __init__(self, scope, id: str, config: PlatformConfig, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.networking = NetworkingConstruct(self, config)
        
        # Export networking outputs
        CfnOutput(
            self,
            "VpcId",
            value=self.networking.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{config.app_name}-vpc-id"
        )
        
        CfnOutput(
            self,
            "SecurityGroupId",
            value=self.networking.security_group.security_group_id,
            description="Security Group ID",
            export_name=f"{config.app_name}-security-group-id"
        )
        
        CfnOutput(
            self,
            "PublicSubnetIds",
            value=",".join([subnet.subnet_id for subnet in self.networking.vpc.public_subnets]),
            description="Public Subnet IDs",
            export_name=f"{config.app_name}-public-subnet-ids"
        )
        
        CfnOutput(
            self,
            "PrivateSubnetIds",
            value=",".join([subnet.subnet_id for subnet in self.networking.vpc.private_subnets]),
            description="Private Subnet IDs",
            export_name=f"{config.app_name}-private-subnet-ids"
        )

class ContainerStack(Stack):
    """Container infrastructure stack."""
    
    def __init__(self, scope, id: str, config: PlatformConfig, networking_stack: NetworkingStack, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.container = ContainerConstruct(
            self, 
            config,
            vpc=networking_stack.networking.vpc,
            security_group=networking_stack.networking.security_group
        )
        
        # Export container outputs
        CfnOutput(
            self,
            "EcrRepositoryName",
            value=self.container.repository.repository_name,
            description="ECR Repository Name",
            export_name=f"{config.app_name}-ecr-repository-name"
        )
        
        CfnOutput(
            self,
            "EcsClusterName",
            value=self.container.cluster.cluster_name,
            description="ECS Cluster Name",
            export_name=f"{config.app_name}-ecs-cluster-name"
        )
        
        CfnOutput(
            self,
            "EcsServiceName",
            value=self.container.service.service_name,
            description="ECS Service Name",
            export_name=f"{config.app_name}-ecs-service-name"
        )

# Create CDK app
app = App()

# Load configuration
config = PlatformConfig()

# Create the environment
env = Environment(
    account=config.account_id,
    region=config.region
)

# Create stacks
networking_stack = NetworkingStack(app, "NetworkingStack", config, env=env)
container_stack = ContainerStack(app, "ContainerStack", config, networking_stack, env=env)

# Add dependency
container_stack.add_dependency(networking_stack)

app.synth() 