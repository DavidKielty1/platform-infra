from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_logs as logs,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
    Tags
)
from constructs import Construct
from src.utils.config import PlatformConfig

class ContainerConstruct(Construct):
    """Container infrastructure for the platform."""
    
    def __init__(
        self,
        scope: Construct,
        config: PlatformConfig,
        vpc: ec2.IVpc,
        security_group: ec2.ISecurityGroup
    ) -> None:
        super().__init__(scope, "ContainerConstruct")
        
        self.config = config
        self.vpc = vpc
        self.security_group = security_group
        
        # Create KMS key for log encryption
        self.log_key = kms.Key(
            self,
            "LogEncryptionKey",
            description="KMS key for CloudWatch Logs encryption",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create CloudWatch Log Group with KMS encryption
        self.log_group = logs.LogGroup(
            self,
            "ApplicationContainerLogGroup",
            log_group_name=f"/ecs/{self.config.app_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            encryption_key=self.log_key,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create ECR repository
        self.repository = self._create_repository()
        
        # Create ECS cluster
        self.cluster = self._create_cluster()
        
        # Create task execution role
        self.task_execution_role = self._create_task_execution_role()
        
        # Create task role
        self.task_role = self._create_task_role()
        
        # Create ECS task definition
        self.task_definition = self._create_task_definition()
        
        # Create ECS service
        self.service = self._create_service()
        
        # Add tags
        self._add_tags()
    
    def _create_repository(self) -> ecr.Repository:
        """Import the existing ECR repository for the application."""
        return ecr.Repository.from_repository_name(
            self,
            "ApplicationRepository",
            repository_name=f"{self.config.app_name}-repo"
        )
    
    def _create_cluster(self) -> ecs.Cluster:
        """Create an ECS cluster."""
        return ecs.Cluster(
            self,
            "ApplicationCluster",
            cluster_name=self.config.ecs_cluster_name,
            vpc=self.vpc,
            container_insights=True
        )
    
    def _create_task_execution_role(self) -> iam.Role:
        """Create the task execution role for ECS tasks."""
        role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for ECS task execution"
        )
        
        # Add policy for pulling images from ECR
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )
        
        # Add policy for CloudWatch Logs
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=[self.log_group.log_group_arn]
            )
        )
        
        return role
    
    def _create_task_role(self) -> iam.Role:
        """Create the task role for ECS tasks."""
        role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="Role for ECS task execution"
        )
        
        # Add minimal permissions needed for the application
        role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                resources=["*"]
            )
        )
        
        return role
    
    def _create_task_definition(self) -> ecs.FargateTaskDefinition:
        """Create a Fargate task definition."""
        task_definition = ecs.FargateTaskDefinition(
            self,
            "ApplicationTaskDefinition",
            family=f"{self.config.app_name}-task",
            cpu=self.config.ecs_task_cpu,
            memory_limit_mib=self.config.ecs_task_memory,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.X86_64
            ),
            execution_role=self.task_execution_role,
            task_role=self.task_role
        )
        
        # Add container to the task definition
        task_definition.add_container(
            "ApplicationContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                self.repository,
                tag="latest"
            ),
            container_name=self.config.app_name,
            port_mappings=[
                ecs.PortMapping(
                    container_port=self.config.container_port,
                    host_port=self.config.container_port,
                    protocol=ecs.Protocol.TCP
                )
            ],
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=self.config.app_name,
                log_group=self.log_group
            ),
            environment={
                "APP_ENV": self.config.app_env,
                "APP_PORT": str(self.config.container_port)
            },
            health_check={
                "command": [
                    "CMD-SHELL",
                    f"wget --no-verbose --tries=1 --spider http://localhost:{self.config.container_port}/health || exit 1"
                ],
                "interval": Duration.seconds(30),
                "timeout": Duration.seconds(5),
                "retries": 3,
                "start_period": Duration.seconds(60)
            }
        )
        
        return task_definition
    
    def _create_service(self) -> ecs.FargateService:
        """Create a Fargate service."""
        return ecs.FargateService(
            self,
            "ApplicationService",
            service_name=self.config.ecs_service_name,
            cluster=self.cluster,
            task_definition=self.task_definition,
            desired_count=self.config.ecs_desired_count,
            assign_public_ip=True,
            security_groups=[self.security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )
    
    def _add_tags(self) -> None:
        """Add tags to the container resources."""
        for resource in [self.repository, self.cluster, self.service, self.log_key, self.task_execution_role, self.task_role]:
            Tags.of(resource).add("Environment", self.config.environment)
            Tags.of(resource).add("Project", self.config.project)
            Tags.of(resource).add("Team", self.config.team)