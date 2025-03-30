# Infrastructure Constructs

## Overview
This directory contains documentation for the reusable CDK constructs used in the platform. These constructs are designed to be modular and reusable across different stacks.

## Container Construct

The `ContainerConstruct` creates container-related resources:

### Components
1. **ECR Repository**
   ```python
   # Creation
   repository = ecr.Repository(self, "ApplicationRepository",
       repository_name=repository_name,
       removal_policy=RemovalPolicy.DESTROY,
       auto_delete_images=True
   )
   ```

2. **ECS Cluster**
   ```python
   # Creation
   cluster = ecs.Cluster(self, "ApplicationCluster",
       cluster_name=cluster_name,
       vpc=vpc
   )
   ```

3. **Fargate Service**
   ```python
   # Creation
   service = ecs.FargateService(self, "ApplicationService",
       cluster=cluster,
       task_definition=task_definition,
       service_name=service_name
   )
   ```

### Known Issues

1. **Repository Deletion**
   - Issue: Cannot delete repository with images
   - Solution: Use `auto_delete_images=True` or force delete

2. **Service Updates**
   - Issue: Service update failures
   - Solution: Implement proper health checks

### Best Practices

1. **Resource Cleanup**
   ```python
   # Always set removal policy
   RemovalPolicy.DESTROY
   
   # Enable auto delete for repositories
   auto_delete_images=True
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

The `NetworkConstruct` creates networking resources:

### Components
1. **VPC**
   ```python
   # Creation
   vpc = ec2.Vpc(self, "ApplicationVPC",
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
               subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
               cidr_mask=24
           )
       ]
   )
   ```

2. **Security Groups**
   ```python
   # Creation
   security_group = ec2.SecurityGroup(self, "ApplicationSecurityGroup",
       vpc=vpc,
       security_group_name=f"{config.app_name}-sg",
       description="Security group for application"
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
   # Creation
   log_group = logs.LogGroup(self, "ApplicationLogGroup",
       log_group_name=f"/ecs/{config.app_name}",
       retention=logs.RetentionDays.ONE_MONTH,
       removal_policy=RemovalPolicy.DESTROY
   )
   ```

2. **Alarms**
   ```python
   # Creation
   alarm = cloudwatch.Alarm(self, "HighCPUAlarm",
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
   container = ContainerConstruct(self, "Container",
       vpc=network.vpc,
       config=config
   )
   ```

2. **Network Construct**
   ```python
   network = NetworkConstruct(self, "Network",
       config=config
   )
   ```

3. **Monitoring Construct**
   ```python
   monitoring = MonitoringConstruct(self, "Monitoring",
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