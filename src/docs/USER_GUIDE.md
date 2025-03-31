# User Guide

## Overview
This guide is for application developers using the platform. It covers how to deploy and manage your containerized applications using our infrastructure.

## Quick Start

1. **Prerequisites**
   - Docker Desktop
   - VS Code with Dev Containers
   - Git

2. **Initial Setup**
   ```bash
   # Clone repository
   git clone <repo-url>
   cd platform
   
   # Install pre-commit hooks
   pip install pre-commit
   pre-commit install
   
   # Start development container
   docker-compose up -d
   ```

3. **Open in VS Code**
   - Use the Dev Containers extension to open the project in the container

## Application Requirements

Your application should:
- Be containerized
- Expose a port (default: 5000)
- Include a health check endpoint
- Log to stdout/stderr
- Use environment variables for configuration

## Development Workflow

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   - Write your code
   - Add tests
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```
   Note: Pre-commit hooks will run automatically

4. **Push Changes**
   ```bash
   git push origin feature/your-feature
   ```

## Code Quality Tools

The platform provides pre-commit hooks for:
- Basic file checks
- Python formatting (black)
- Import sorting (isort)
- Basic linting (flake8)
- Docker linting (hadolint)
- Infrastructure security (checkov)

## VS Code Extensions

Recommended extensions:
- Python and Pylance
- Black formatter
- Flake8 linter
- isort
- MyPy type checker
- Docker
- GitLens
- Markdown support
- YAML support
- Terraform
- AWS Toolkit

## Environment Variables

Required variables:
```env
# AWS Configuration
AWS_REGION=eu-west-2
AWS_ACCOUNT_ID=your_account_id

# Application Configuration
APP_NAME=your-app-name
APP_ENV=development
APP_PORT=5000
```

## Troubleshooting

If you encounter issues:

1. **Pre-commit Hooks**
   ```bash
   # Run hooks manually
   pre-commit run --all-files
   
   # Skip hooks temporarily
   git commit -m "message" --no-verify
   ```

2. **Container Issues**
   ```bash
   # Check container logs
   docker-compose logs
   
   # Restart container
   docker-compose restart
   ```

3. **Deployment Issues**
   - Check AWS credentials
   - Verify environment variables
   - Review CloudWatch logs
   - Check ECS service status

## Support

For issues or questions:
1. Check this documentation
2. Review CloudWatch logs
3. Contact platform team 