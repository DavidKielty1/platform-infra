# Platform Infrastructure

A pre-configured AWS infrastructure setup for deploying containerized applications to AWS ECS (Elastic Container Service). This platform provides a standardized way to deploy and manage containerized applications with proper networking, security, and monitoring.

## Quick Start

1. **Prerequisites**
   - Docker Desktop
   - VS Code with Dev Containers
   - Git

2. **Local Development**
   ```bash
   # Clone repository
   git clone <repo-url>
   
   # Open in VS Code
   code .
   
   # Reopen in container
   # (VS Code will prompt)
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
.
├── devex/                    # Developer Experience tools
│   ├── tools/               # Development tools
│   │   ├── code-quality/    # Code quality configurations
│   │   └── cicd/           # CI/CD templates
├── infrastructure/          # AWS CDK infrastructure code
│   ├── src/                # CDK source code
│   │   ├── constructs/     # Reusable CDK constructs
│   │   └── stacks/        # CDK stacks
│   └── scripts/           # Deployment scripts
├── docs/                   # Documentation
└── tests/                 # Test suite
```

## Key Features

1. **Infrastructure**
   - Container registry (ECR)
   - Container orchestration (ECS)
   - Networking (VPC, subnets)
   - Security (IAM, security groups)
   - Monitoring (CloudWatch)

2. **Development Experience**
   - Pre-configured development containers
   - Code quality tools
   - CI/CD templates
   - Security scanning

## Documentation

- [User Guide](docs/USER_GUIDE.md) - For application developers
- [Infrastructure Documentation](docs/infrastructure/README.md) - For platform engineers
- [Technical Documentation](docs/Documentation.md) - For implementation details

## Contributing

1. Create feature branch
2. Make changes
3. Run tests
4. Create PR
5. Get review
6. Merge to main

## Support

For issues or questions, contact the platform team.