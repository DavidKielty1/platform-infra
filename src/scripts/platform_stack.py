from aws_cdk import Stack, CfnOutput
from constructs import Construct
from .networking import NetworkingConstruct
from .container import ContainerConstruct
from ..utils.config import PlatformConfig

class PlatformStack(Stack):
    """Platform stack that creates all necessary infrastructure."""
    
    def __init__(self, scope: Construct, construct_id: str, config: PlatformConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Store configuration
        self.config = config
        
        # Create networking infrastructure
        networking = NetworkingConstruct(self, config)
        
        # Output networking information
        self._output_networking_info(networking.vpc, networking.security_group)
        
        # If we're only deploying networking, stop here
        if config.deploy_networking_only:
            return
            
        # Create container infrastructure
        container = ContainerConstruct(
            self,
            config,
            vpc=networking.vpc,
            security_group=networking.security_group
        )
        
        # Output container information
        self._output_container_info(
            cluster=container.cluster,
            service=container.service,
            repository=container.repository
        )
    
    def _output_networking_info(self, vpc, security_group):
        """Output networking information."""
        CfnOutput(self, "VpcId", value=vpc.vpc_id)
        CfnOutput(self, "SecurityGroupId", value=security_group.security_group_id)
        CfnOutput(self, "PublicSubnets", value=','.join([s.subnet_id for s in vpc.public_subnets]))
        CfnOutput(self, "PrivateSubnets", value=','.join([s.subnet_id for s in vpc.private_subnets]))
    
    def _output_container_info(self, cluster, service, repository):
        """Output container information."""
        CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        CfnOutput(self, "ServiceName", value=service.service_name)
        CfnOutput(self, "RepositoryUri", value=repository.repository_uri) 