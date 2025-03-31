#!/bin/bash

# Phased deployment script for infrastructure

echo -e "\033[32mStarting phased deployment...\033[0m"

# Function to handle errors
handle_error() {
    echo -e "\033[31mERROR: $1\033[0m"
    exit 1
}

# Function to check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &>/dev/null; then
        handle_error "AWS credentials not found or invalid. Please configure your AWS credentials."
    fi
}

# Check AWS credentials before starting
echo "Checking AWS credentials..."
check_aws_credentials

# Phase 1: Deploy VPC and Networking
echo -e "\n\033[33mPhase 1: Deploying VPC and Networking...\033[0m"
echo "This phase will create the VPC, subnets, and networking components using NetworkingStack."
read -p "Press Enter to continue with Phase 1 (or Ctrl+C to cancel)..."

# First synthesize to check for errors
echo "Synthesizing NetworkingStack..."
npx cdk synth NetworkingStack --app "py app.py" || handle_error "Failed to synthesize networking stack"

# Deploy networking stack
echo "Deploying NetworkingStack..."
npx cdk deploy NetworkingStack --app "py app.py" --require-approval never || handle_error "Failed to deploy networking stack"
echo -e "\033[32mPhase 1 completed successfully!\033[0m"

# Wait for networking resources to be fully available
echo "Waiting for 30 seconds to ensure networking resources are ready..."
sleep 30

# Phase 2: Deploy Container Infrastructure
echo -e "\n\033[33mPhase 2: Deploying Container Infrastructure...\033[0m"
echo "This phase will create the ECR repository, ECS cluster, and related resources using ContainerStack."
read -p "Press Enter to continue with Phase 2 (or Ctrl+C to cancel)..."

# First synthesize to check for errors
echo "Synthesizing ContainerStack..."
npx cdk synth ContainerStack --app "py app.py" || handle_error "Failed to synthesize container stack"

# Deploy container stack
echo "Deploying ContainerStack..."
npx cdk deploy ContainerStack --app "py app.py" --require-approval never || handle_error "Failed to deploy container stack"
echo -e "\033[32mPhase 2 completed successfully!\033[0m"

echo -e "\n\033[32mPhased deployment completed successfully!\033[0m"
echo "Next steps:"
echo "1. Build your container image"
echo "2. Push the image to the ECR repository"
echo "3. The ECS service will automatically deploy your application" 