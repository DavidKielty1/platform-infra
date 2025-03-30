import boto3
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add infrastructure directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.config import PlatformConfig

def print_section(title):
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")

def check_vpc():
    ec2 = boto3.client('ec2')
    config = PlatformConfig.from_env()
    
    print_section("VPC Information")
    try:
        # List all VPCs and find the one with our tags
        vpcs = ec2.describe_vpcs(
            Filters=[
                {'Name': 'tag:Project', 'Values': [config.project]},
                {'Name': 'tag:Environment', 'Values': [config.environment]}
            ]
        )['Vpcs']
        
        if not vpcs:
            print("No VPC found with matching tags. Resources might still be creating...")
            return
        
        vpc = vpcs[0]
        print(f"VPC ID: {vpc['VpcId']}")
        print(f"CIDR Block: {vpc['CidrBlock']}")
        print(f"State: {vpc['State']}")
        
        # Get subnet details
        subnet_response = ec2.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}]
        )
        
        print_section("Subnet Information")
        for subnet in subnet_response['Subnets']:
            print(f"\nSubnet ID: {subnet['SubnetId']}")
            print(f"Availability Zone: {subnet['AvailabilityZone']}")
            print(f"CIDR Block: {subnet['CidrBlock']}")
            print(f"State: {subnet['State']}")
            print(f"Public: {subnet['MapPublicIpOnLaunch']}")
    except Exception as e:
        print(f"Error checking VPC: {str(e)}")
        print("Resources might still be creating...")

def check_ecs():
    ecs = boto3.client('ecs')
    config = PlatformConfig.from_env()
    
    print_section("ECS Cluster Information")
    try:
        # Get cluster details
        cluster_response = ecs.describe_clusters(clusters=[config.ecs_cluster_name])
        if not cluster_response['clusters']:
            print("No ECS cluster found. Resources might still be creating...")
            return
            
        cluster = cluster_response['clusters'][0]
        print(f"Cluster Name: {cluster['clusterName']}")
        print(f"Status: {cluster['status']}")
        print(f"Running Tasks: {cluster['runningTasksCount']}")
        print(f"Pending Tasks: {cluster['pendingTasksCount']}")
        
        # Get service details
        service_response = ecs.describe_services(
            cluster=config.ecs_cluster_name,
            services=[config.ecs_service_name]
        )
        if not service_response['services']:
            print("No ECS service found. Resources might still be creating...")
            return
            
        service = service_response['services'][0]
        print_section("ECS Service Information")
        print(f"Service Name: {service['serviceName']}")
        print(f"Status: {service['status']}")
        print(f"Desired Count: {service['desiredCount']}")
        print(f"Running Count: {service['runningCount']}")
        print(f"Pending Count: {service['pendingCount']}")
        
        # Get task definition
        task_def_response = ecs.describe_task_definition(
            taskDefinition=service['taskDefinition']
        )
        task_def = task_def_response['taskDefinition']
        
        print_section("Task Definition Information")
        print(f"Family: {task_def['family']}")
        print(f"Revision: {task_def['revision']}")
        print(f"Status: {task_def['status']}")
        print(f"CPU: {task_def['cpu']}")
        print(f"Memory: {task_def['memory']}")
        
        # Print container details
        for container in task_def['containerDefinitions']:
            print(f"\nContainer Name: {container['name']}")
            print(f"Image: {container['image']}")
            print(f"Port Mappings: {json.dumps(container.get('portMappings', []), indent=2)}")
    except Exception as e:
        print(f"Error checking ECS: {str(e)}")
        print("Resources might still be creating...")

def check_ecr():
    ecr = boto3.client('ecr')
    config = PlatformConfig.from_env()
    
    print_section("ECR Repository Information")
    try:
        repo_response = ecr.describe_repositories(repositoryNames=[config.ecr_repo_name])
        repo = repo_response['repositories'][0]
        print(f"Repository Name: {repo['repositoryName']}")
        print(f"Repository URI: {repo['repositoryUri']}")
        print(f"Created At: {repo['createdAt']}")
    except ecr.exceptions.RepositoryNotFoundException:
        print("Repository not found! Resources might still be creating...")
    except Exception as e:
        print(f"Error checking ECR: {str(e)}")
        print("Resources might still be creating...")

def check_security_groups():
    ec2 = boto3.client('ec2')
    config = PlatformConfig.from_env()
    
    print_section("Security Group Information")
    try:
        # Find security group by tags
        security_groups = ec2.describe_security_groups(
            Filters=[
                {'Name': 'tag:Project', 'Values': [config.project]},
                {'Name': 'tag:Environment', 'Values': [config.environment]}
            ]
        )['SecurityGroups']
        
        if not security_groups:
            print("No security groups found with matching tags. Resources might still be creating...")
            return
            
        for sg in security_groups:
            print(f"\nSecurity Group ID: {sg['GroupId']}")
            print(f"Group Name: {sg['GroupName']}")
            print(f"Description: {sg['Description']}")
            print("\nInbound Rules:")
            for rule in sg['IpPermissions']:
                print(f"- Protocol: {rule.get('IpProtocol', 'all')}")
                print(f"  From Port: {rule.get('FromPort', 'all')}")
                print(f"  To Port: {rule.get('ToPort', 'all')}")
                print(f"  IP Ranges: {[ip['CidrIp'] for ip in rule.get('IpRanges', [])]}")
    except Exception as e:
        print(f"Error checking security groups: {str(e)}")
        print("Resources might still be creating...")

def main():
    try:
        check_vpc()
        check_ecs()
        check_ecr()
        check_security_groups()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 