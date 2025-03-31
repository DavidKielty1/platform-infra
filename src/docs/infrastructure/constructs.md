# Infrastructure Constructs

## Overview
This directory contains documentation for the reusable CDK constructs used in the platform. These constructs are designed to be modular and reusable across different stacks.

## Container Construct

The `ContainerConstruct` creates container-related resources:

### Components
1. **ECR Repository**
   ```python
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
   ```

2. **ECS Cluster**
   ```python
   cluster = ecs.Cluster(
       self,
       "ApplicationCluster",
       cluster_name=config.ecs_cluster_name,
       vpc=vpc,
       container_insights=True
   )
   ```

3. **Task Definition**
   ```python
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
   ```

4. **ECS Service**
   ```python
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
   ```

### Known Issues

1. **Repository Deletion**
   - Issue: Cannot delete repository with images
   - Solution: Use `empty_on_delete=True` or force delete

2. **Service Updates**
   - Issue: Service update failures
   - Solution: Implement proper health checks

### Best Practices

1. **Resource Cleanup**
   ```python
   # Always set removal policy
   RemovalPolicy.DESTROY
   
   # Enable auto delete for repositories
   empty_on_delete=True
   ```

2. **Health Checks**
   ```python
   # Implement proper health checks
   health_check = ecs.HealthCheck(
       command=["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
       interval=Duration.seconds(30),
       timeout=Duration.seconds(5),
       retries=3
   )
   ```

## Network Construct

The `NetworkingConstruct` creates networking resources:

### Components
1. **VPC**
   ```python
   vpc = ec2.Vpc(
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
   ```

2. **Security Groups**
   ```python
   security_group = ec2.SecurityGroup(
       self,
       "ApplicationSecurityGroup",
       vpc=vpc,
       description="Security group for application resources",
       allow_all_outbound=True
   )
   ```

### Best Practices

1. **VPC Design**
   - Use multiple AZs for high availability
   - Implement proper CIDR planning
   - Use private subnets for containers

2. **Security Groups**
   - Follow least privilege principle
   - Document all rules
   - Regular review and cleanup

## Monitoring Construct

The `MonitoringConstruct` creates monitoring resources:

### Components
1. **CloudWatch Logs**
   ```python
   log_group = logs.LogGroup(
       self,
       "ContainerLogGroup",
       log_group_name=f"/ecs/{config.app_name}",
       retention=logs.RetentionDays.ONE_WEEK,
       encryption_key=log_key,
       removal_policy=RemovalPolicy.DESTROY
   )
   ```

2. **Alarms**
   ```python
   alarm = cloudwatch.Alarm(
       self,
       "HighCPUAlarm",
       metric=service.metric_cpu_utilization(),
       threshold=80,
       evaluation_periods=3,
       datapoints_to_alarm=2
   )
   ```

### Best Practices

1. **Logging**
   - Set appropriate retention periods
   - Use structured logging
   - Implement log rotation

2. **Metrics**
   - Monitor key performance indicators
   - Set appropriate thresholds
   - Implement proper alerting

## Usage Examples

1. **Container Construct**
   ```python
   container = ContainerConstruct(
       self,
       "Container",
       config=config,
       vpc=network.vpc,
       security_group=network.security_group
   )
   ```

2. **Network Construct**
   ```python
   network = NetworkConstruct(
       self,
       "Network",
       config=config
   )
   ```

3. **Monitoring Construct**
   ```python
   monitoring = MonitoringConstruct(
       self,
       "Monitoring",
       service=container.service,
       config=config
   )
   ```

## Testing

1. **Unit Tests**
   ```python
   # Test construct creation
   def test_container_construct():
       stack = Stack()
       container = ContainerConstruct(stack, "Test")
       template = Template.from_stack(stack)
       template.has_resource("AWS::ECR::Repository")
   ```

2. **Integration Tests**
   ```python
   # Test construct integration
   def test_construct_integration():
       stack = Stack()
       network = NetworkConstruct(stack, "Network")
       container = ContainerConstruct(stack, "Container", vpc=network.vpc)
       template = Template.from_stack(stack)
       template.has_resource("AWS::ECS::Service")
   ``` 