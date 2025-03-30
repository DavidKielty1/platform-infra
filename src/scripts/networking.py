from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
    Stack,
    CfnOutput,
    Tags
)
from constructs import Construct
from ..utils.config import PlatformConfig

class NetworkingConstruct(Construct):
    """Networking infrastructure for the platform."""
    
    def __init__(self, scope: Construct, config: PlatformConfig) -> None:
        super().__init__(scope, "NetworkingConstruct")
        
        self.config = config
        
        # Create VPC if new resources are to be created
        if config.create_new_resources:
            # Create IAM role for VPC Flow Logs
            flow_logs_role = iam.Role(
                self,
                "FlowLogsRole",
                assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
                description="IAM role for VPC Flow Logs",
            )
            flow_logs_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonVPCFlowLogsRole")
            )

            # Create IAM role for KMS key administrators
            kms_admin_role = iam.Role(
                self,
                "KMSAdminRole",
                assumed_by=iam.ServicePrincipal("kms.amazonaws.com"),
                description="IAM role for KMS key administrators",
            )
            kms_admin_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSKMSAdministrator")
            )

            # Create IAM role for KMS key users
            kms_user_role = iam.Role(
                self,
                "KMSUserRole",
                assumed_by=iam.ServicePrincipal("cloudwatch.amazonaws.com"),
                description="IAM role for KMS key users",
            )
            kms_user_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/CloudWatchLogsRole")
            )

            self.vpc = ec2.Vpc(
                self,
                "PlatformVPC",
                max_azs=2,
                nat_gateways=1,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name="Public",
                        subnet_type=ec2.SubnetType.PUBLIC,
                    ),
                    ec2.SubnetConfiguration(
                        name="Private",
                        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    ),
                ],
                enable_dns_hostnames=True,
                enable_dns_support=True,
                flow_logs={
                    "FlowLogs": ec2.FlowLogOptions(
                        destination=ec2.FlowLogDestination.to_cloud_watch_logs(flow_logs_role),
                        traffic_type=ec2.FlowLogTrafficType.ALL,
                        max_aggregation_interval=Duration.seconds(600)
                    )
                },
                ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16")
            )

            # Create security group for application
            self.security_group = ec2.SecurityGroup(
                self,
                "ApplicationSecurityGroup",
                vpc=self.vpc,
                description="Security group for application resources",
                allow_all_outbound=False,  # Restrict outbound traffic
            )

            # Add VPC endpoints for AWS services
            self.vpc.add_interface_endpoint(
                "SecretsManagerEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
                security_groups=[self.security_group]
            )
            self.vpc.add_interface_endpoint(
                "SSMEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.SSM,
                security_groups=[self.security_group]
            )
            self.vpc.add_interface_endpoint(
                "SSMMessagesEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES,
                security_groups=[self.security_group]
            )
            self.vpc.add_interface_endpoint(
                "CloudWatchLogsEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
                security_groups=[self.security_group]
            )
            self.vpc.add_interface_endpoint(
                "KMSEndpoint",
                service=ec2.InterfaceVpcEndpointAwsService.KMS,
                security_groups=[self.security_group]
            )

            # Create KMS key for log encryption
            log_key = kms.Key(
                self,
                "LogEncryptionKey",
                enable_key_rotation=True,
                description="KMS key for encrypting CloudWatch logs",
                alias=f"NetworkingConstruct-log-key",
                pending_window=Duration.days(7),  # Deletion window
                removal_policy=RemovalPolicy.RETAIN,  # Prevent accidental deletion
                key_spec=kms.KeySpec.SYMMETRIC_DEFAULT,
                key_usage=kms.KeyUsage.ENCRYPT_DECRYPT,
                key_administrators=[kms_admin_role],
                key_users=[kms_user_role]
            )

            # Add tags to resources
            Tags.of(self.vpc).add("Name", "NetworkingConstruct-vpc")
            Tags.of(self.security_group).add("Name", f"{config.project_name}-app-sg")
            Tags.of(log_key).add("Name", "NetworkingConstruct-log-key")

            # Output values
            CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
            CfnOutput(self, "SecurityGroupId", value=self.security_group.security_group_id)
            CfnOutput(self, "LogKeyArn", value=log_key.key_arn)
        else:
            # Look up existing VPC
            self.vpc = ec2.Vpc.from_lookup(
                self,
                "ExistingVPC",
                vpc_id=config.vpc_id,
            )
        
        # Create security group for application if not already created
        if not hasattr(self, 'security_group'):
            self.security_group = ec2.SecurityGroup(
                self,
                "ApplicationSecurityGroup",
                vpc=self.vpc,
                description="Security group for application resources",
                allow_all_outbound=False,  # Restrict outbound traffic
            )
        
        # Add specific outbound rules with descriptions
        self.security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS outbound traffic",
        )
        self.security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP outbound traffic",
        )

        # Add specific inbound rules with descriptions
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS inbound traffic",
        )
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP inbound traffic",
        )
        
        # Add tags
        self._add_tags()
    
    def _add_tags(self) -> None:
        """Add tags to the networking resources."""
        for resource in [self.vpc, self.security_group]:
            Tags.of(resource).add("Environment", self.config.environment)
            Tags.of(resource).add("Project", self.config.project)
            Tags.of(resource).add("Team", self.config.team) 