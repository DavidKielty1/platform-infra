from aws_cdk import (
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_logs as logs,
    aws_kms as kms,
    aws_ec2 as ec2,
    RemovalPolicy,
    Stack
)
from constructs import Construct
from scripts.config import PlatformConfig

class ContainerConstruct(Construct):
    """Container infrastructure construct."""
    
    def __init__(self, scope: Construct, config: PlatformConfig, vpc, security_group, **kwargs):
        super().__init__(scope, "ContainerConstruct", **kwargs)
        
        # Create KMS key for log encryption
        log_key = kms.Key(
            self,
            "LogEncryptionKey",
            description="KMS key for CloudWatch Logs encryption",
            enable_key_rotation=True
        )
        
        # Grant CloudWatch Logs permission to use the key
        log_key.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("logs.eu-west-2.amazonaws.com")],
                actions=[
                    "kms:Encrypt*",
                    "kms:Decrypt*",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:Describe*"
                ],
                resources=["*"],
                conditions={
                    "ArnLike": {
                        "kms:EncryptionContext:aws:logs:arn": f"arn:aws:logs:eu-west-2:{Stack.of(self).account}:*"
                    }
                }
            )
        )
        
        # Create CloudWatch Log Group with KMS encryption
        log_group = logs.LogGroup(
            self,
            "ContainerLogGroup",
            log_group_name=f"/ecs/{config.app_name}",
            retention=logs.RetentionDays.ONE_DAY,
            encryption_key=log_key,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create ECR repository
        repository = ecr.Repository(
            self,
            "ApplicationRepository",
            repository_name=config.app_name,
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True,
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Keep only the last 5 images",
                    max_image_count=5
                )
            ]
        )
        
        # Create ECS cluster
        cluster = ecs.Cluster(
            self,
            "ApplicationCluster",
            cluster_name=config.ecs_cluster_name,
            vpc=vpc,
            container_insights=True
        )
        
        # Create task execution role
        task_execution_role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        # Add policy for task execution
        task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )
        
        # Create task role
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        # Add basic policy for task role
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess")
        )
        
        # Create task definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "ApplicationTaskDefinition",
            execution_role=task_execution_role,
            task_role=task_role,
            memory_limit_mib=config.ecs_task_memory,
            cpu=config.ecs_task_cpu,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.X86_64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX
            )
        )
        
        # Add container to task
        container = task_definition.add_container(
            "ApplicationContainer",
            image=ecs.ContainerImage.from_ecr_repository(repository),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="ecs",
                log_group=log_group
            ),
            port_mappings=[ecs.PortMapping(container_port=config.container_port)]
        )
        
        # Create ECS service
        service = ecs.FargateService(
            self,
            "ApplicationService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            security_groups=[security_group],
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
        
        # Store references
        self.cluster = cluster
        self.service = service
        self.repository = repository