import os
import json
from typing import List, Optional

class PlatformConfig:
    """Platform configuration settings."""
    
    def __init__(self, env_vars: dict):
        # AWS Configuration
        self.account_id = env_vars.get("AWS_ACCOUNT_ID", "")
        self.region = env_vars.get("AWS_REGION", "eu-west-2")
        self.aws_access_key_id = env_vars.get("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key = env_vars.get("AWS_SECRET_ACCESS_KEY", "")
        
        # Application Configuration
        self.app_name = env_vars.get("APP_NAME", "platform-demo")
        self.app_env = env_vars.get("APP_ENV", "development")
        self.app_port = int(env_vars.get("APP_PORT", "5000"))
        
        # Network Configuration
        self.vpc_cidr = env_vars.get("VPC_CIDR", "10.0.0.0/16")
        self.availability_zones = env_vars.get("AVAILABILITY_ZONES", "eu-west-2a,eu-west-2b").split(",")
        self.vpc_id = env_vars.get("VPC_ID")
        self._subnet_ids = env_vars.get("SUBNET_IDS", "").split(",") if env_vars.get("SUBNET_IDS") else None
        self._security_group_ids = env_vars.get("SECURITY_GROUP_IDS", "").split(",") if env_vars.get("SECURITY_GROUP_IDS") else None
        
        # ECS Configuration
        self.ecs_cluster_name = env_vars.get("ECS_CLUSTER_NAME", "platform-cluster")
        self.ecs_service_name = env_vars.get("ECS_SERVICE_NAME", "platform-service")
        self.ecs_task_cpu = int(env_vars.get("ECS_TASK_CPU", "256"))
        self.ecs_task_memory = int(env_vars.get("ECS_TASK_MEMORY", "512"))
        self.ecs_desired_count = int(env_vars.get("ECS_DESIRED_COUNT", "1"))
        
        # Container Configuration
        self.container_port = int(env_vars.get("CONTAINER_PORT", "5000"))
        self.container_cpu = int(env_vars.get("CONTAINER_CPU", "256"))
        self.container_memory = int(env_vars.get("CONTAINER_MEMORY", "512"))
        
        # Deployment Configuration
        self.deploy_networking_only = env_vars.get("DEPLOY_NETWORKING_ONLY", "false").lower() == "true"
        self.create_new_resources = env_vars.get("CREATE_NEW_RESOURCES", "true").lower() == "true"
        
        # Resource Tags
        self.environment = env_vars.get("APP_ENV", "development")
        self.project = env_vars.get("PROJECT", "platform")
        self.team = env_vars.get("TEAM", "platform")
    
    @classmethod
    def from_env(cls) -> "PlatformConfig":
        """Create a PlatformConfig instance from environment variables."""
        env_vars = dict(os.environ)
        return cls(env_vars)

    @property
    def ecr_repo_name(self) -> str:
        """Get ECR repository name."""
        return f"{self.app_name}-repo"
        
    @property
    def subnet_ids(self) -> List[str]:
        """Get subnet IDs."""
        return self._subnet_ids if self._subnet_ids else []
        
    @property
    def security_group_ids(self) -> List[str]:
        """Get security group IDs."""
        return self._security_group_ids if self._security_group_ids else [] 