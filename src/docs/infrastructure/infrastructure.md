# Infrastructure Documentation

## Overview
This directory contains AWS CDK infrastructure code and related documentation for the platform. The infrastructure is designed to provide a robust, secure, and scalable environment for running containerized applications.

## Infrastructure Components

1. **VPC and Networking**
   - VPC with public and private subnets
   - NAT Gateway for private subnet connectivity
   - Security groups for container access
   - Load balancer for traffic distribution

2. **Container Infrastructure**
   - ECS Cluster with Fargate
   - ECR Repository for container images
   - Task definitions for container configuration
   - Service for container orchestration

3. **Security**
   - IAM roles and policies
   - Security groups
   - Secrets management
   - Network isolation

4. **Monitoring and Logging**
   - CloudWatch logs
   - Container insights
   - Health checks
   - Performance metrics

## Directory Structure
```
infrastructure/
├── src/
│   ├── scripts/
│   │   ├── config.py        # Configuration management
│   │   ├── container.py     # Container infrastructure
│   │   ├── networking.py    # Network infrastructure
│   │   └── platform_stack.py # Main stack definition
│   ├── docs/               # Documentation
│   └── app.py              # CDK app entry point
├── .env                    # Environment variables
└── requirements.txt        # Dependencies
```

## Deployment Process

### Prerequisites
- AWS credentials configured
- Docker installed and running
- Node.js and npm for CDK CLI
- Python 3.8+ for CDK application

### Common Deployment Issues and Solutions

1. **Stack in DELETE_FAILED State**
   ```bash
   # Error: Stack is in DELETE_FAILED state and cannot be updated
   # Solution: Clean up resources and redeploy
   
   # 1. Force delete ECR repository if it contains images
   docker-compose run dev aws ecr delete-repository --repository-name platform-repo --force
   
   # 2. Destroy the stack
   docker-compose run dev cdk destroy --force
   
   # 3. Clean up CDK output
   docker-compose run dev rm -rf cdk.out
   
   # 4. Redeploy with no approval prompt
   docker-compose run dev cdk deploy --require-approval never
   ```

2. **Docker Orphan Containers**
   ```bash
   # Clean up orphaned containers regularly
   docker-compose down --remove-orphans
   ```

3. **CDK Output Directory Issues**
   ```bash
   # If you see: "Other CLIs are currently reading from cdk.out"
   docker-compose run dev rm -rf cdk.out
   ```

### Best Practices

1. **Pre-deployment Checks**
   ```python
   # Always verify AWS credentials before deployment
   def verify_aws_credentials():
       print("\nAWS Configuration:")
       print(f"  Region: {os.getenv('AWS_REGION')}")
       print(f"  Account ID: {os.getenv('AWS_ACCOUNT_ID')}")
   ```

2. **Environment Variables**
   - Required variables:
     - AWS_ACCESS_KEY_ID
     - AWS_SECRET_ACCESS_KEY
     - AWS_REGION
     - AWS_ACCOUNT_ID

3. **Deployment Commands**
   ```bash
   # Non-interactive deployment
   docker-compose run dev cdk deploy --require-approval never
   
   # Destroy resources
   docker-compose run dev cdk destroy --force
   ```

4. **Resource Cleanup**
   - Always clean up ECR repositories before deletion
   - Use force flag for stuck resources
   - Keep Docker environment clean
   - Remove CDK output directory if having issues

## Security Considerations

1. **IAM Permissions**
   - Use least privilege principle
   - Review IAM changes during deployment
   - Keep roles and policies minimal

2. **Resource Protection**
   - ECR repositories have deletion protection when containing images
   - Use force delete only when necessary
   - Always backup important data before force operations

## Monitoring and Maintenance

1. **Health Checks**
   ```bash
   # Check ECS service status
   docker-compose run dev aws ecs describe-services \
     --cluster platform-cluster \
     --services platform-service
   ```

2. **Resource Cleanup**
   ```bash
   # Regular cleanup commands
   docker-compose down --remove-orphans
   docker system prune
   ```

## Troubleshooting Guide

1. **Deployment Failures**
   - Check AWS credentials
   - Verify environment variables
   - Clean up orphaned resources
   - Review CloudFormation events

2. **Container Issues**
   - Verify ECR repository exists
   - Check image push permissions
   - Validate task definitions

3. **Network Issues**
   - Verify VPC configuration
   - Check security group rules
   - Validate load balancer health

## Support and Maintenance

For issues or questions:
1. Check this documentation
2. Review CloudFormation events
3. Check ECS service logs
4. Contact platform team if needed

## Separation of Concerns

The project is organized into two main areas of responsibility:

1. **Infrastructure (`/infrastructure`):**
   - AWS CDK code for deploying cloud resources
   - Infrastructure-specific dependencies in `requirements.txt`
   - Focus on AWS services (ECS, ECR, VPC, etc.)
   - Deployment scripts and configuration
   - Infrastructure tests and validation

2. **Developer Experience (`/devex`):**
   - Development environment setup
   - Code quality tools
   - CI/CD pipeline configurations
   - Local development containers
   - Development workflow automation

This separation ensures that:
- Infrastructure code can be deployed independently
- Development tools can be updated without affecting infrastructure
- Each area can have its own dependency management
- Clear responsibility boundaries for maintenance

## Project Structure

```
infrastructure/
├── src/
│   ├── stacks/
│   │   └── platform/          # Platform stack definition
│   ├── constructs/
│   │   ├── networking/        # VPC and security group resources
│   │   └── container/         # ECS and ECR resources
│   └── utils/
│       └── config.py          # Configuration management
├── tests/                     # Test files
├── scripts/
│   ├── deploy/               # Deployment scripts
│   └── cleanup/              # Resource cleanup scripts
└── config/
    ├── dev/                  # Development environment config
    └── prod/                 # Production environment config
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.8 or higher
- Docker installed and running
- VS Code with Dev Containers extension (recommended)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application configuration
APP_NAME=platform-demo
APP_ENV=development
APP_PORT=5000

# AWS configuration
AWS_ACCOUNT_ID=your_account_id
AWS_REGION=eu-west-2

# Deployment configuration
DEPLOY_NETWORKING_ONLY=false
CREATE_NEW_RESOURCES=true

# Network configuration (optional, for existing resources)
VPC_ID=vpc-xxxxxx
SUBNET_IDS=subnet-xxx,subnet-yyy,subnet-zzz
SECURITY_GROUP_IDS=sg-xxxxxx
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd infrastructure
   ```

2. Create and activate virtual environment:
   ```bash
   py -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Bootstrap CDK (first time only):
   ```bash
   cdk bootstrap
   ```

## Deployment

1. Synthesize CloudFormation template:
   ```bash
   cdk synth
   ```

2. Deploy the stack:
   ```bash
   cdk deploy
   ```

3. To deploy only networking components:
   ```bash
   DEPLOY_NETWORKING_ONLY=true cdk deploy
   ```

## Testing

Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=xml
```

## Cleanup

To destroy the stack:
```bash
cdk destroy
```

## Contributing

1. Create a new branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## Security

- Never commit credentials or sensitive information
- Use AWS Secrets Manager for secrets
- Follow least privilege principle
- Review security group rules regularly

## Components

### Networking
- VPC with public/private subnets
- NAT Gateway
- Internet Gateway
- Route tables
- Security groups

### Container Infrastructure
- ECS Cluster
- Fargate services
- Task definitions
- ECR repositories
- Load balancers

### Security
- IAM roles and policies
- Security groups
- Network ACLs
- VPC endpoints

### Monitoring
- CloudWatch logs
- Container insights
- Metrics and alarms
- Health checks

## Configuration

### Environment Variables
- `AWS_REGION`: Target AWS region
- `AWS_ACCOUNT_ID`: AWS account ID
- `ENVIRONMENT`: Deployment environment (dev/staging/prod)

### Infrastructure Parameters
- VPC CIDR: 10.0.0.0/16
- Public subnets: 10.0.1.0/24, 10.0.2.0/24
- Private subnets: 10.0.3.0/24, 10.0.4.0/24
- Container CPU: 256
- Container Memory: 512

## Best Practices

1. **Security**
   - Use least privilege principle
   - Enable encryption at rest
   - Implement proper network isolation
   - Regular security audits

2. **Monitoring**
   - Set up proper logging
   - Configure alerts
   - Monitor costs
   - Track performance metrics

3. **Maintenance**
   - Regular updates
   - Backup strategy
   - Disaster recovery plan
   - Documentation updates

## Cleanup

To remove all resources:
```bash
cdk destroy
```

## Contributing

1. Follow infrastructure as code best practices
2. Update documentation
3. Test changes thoroughly
4. Follow security guidelines

## Sample Application Deployment

The infrastructure includes a sample Flask application deployment to demonstrate the platform's capabilities:

1. **Application Structure**
   ```
   infrastructure/
   └── src/
       └── stacks/
           └── platform/
               └── app.py      # Sample Flask application
   ```

2. **Container Configuration**
   - Port: 3000
   - Health check endpoint: /health
   - Logging: CloudWatch integration
   - Environment variables: Configurable through CDK

3. **Deployment Process**
   ```bash
   # Build and deploy the sample application
   docker-compose run dev cdk deploy --require-approval never
   ```

4. **Verification**
   ```bash
   # Check service status
   aws ecs describe-services --cluster platform-cluster --services platform-service
   
   # View application logs
   aws logs get-log-events --log-group-name /aws/ecs/platform-demo
   ``` 