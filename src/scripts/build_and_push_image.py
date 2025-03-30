import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add the infrastructure directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import PlatformConfig

def load_env_vars():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
    
    # Verify required environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'AWS_ACCOUNT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return PlatformConfig(os.environ)

def verify_aws_credentials():
    """Verify AWS credentials using AWS CLI"""
    print("\nAWS Configuration:")
    print(f"  Region: {os.getenv('AWS_REGION')}")
    print(f"  Account ID: {os.getenv('AWS_ACCOUNT_ID')}")
    print(f"  Access Key ID length: {len(os.getenv('AWS_ACCESS_KEY_ID', ''))}")
    print(f"  Secret Access Key length: {len(os.getenv('AWS_SECRET_ACCESS_KEY', ''))}")

    print("\nEnvironment Variables:")
    print(f"  AWS_ACCESS_KEY_ID: {'*' * len(os.getenv('AWS_ACCESS_KEY_ID', ''))}")
    print(f"  AWS_SECRET_ACCESS_KEY: {'*' * len(os.getenv('AWS_SECRET_ACCESS_KEY', ''))}")
    print(f"  AWS_DEFAULT_REGION: {os.getenv('AWS_REGION')}")

    try:
        # Use AWS CLI to verify credentials
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            env=os.environ
        )
        if result.returncode != 0:
            print(f"\nFailed to verify AWS credentials: {result.stderr}")
            return False
        print(f"\nAWS credentials verified successfully:\n{result.stdout}")
        return True
    except Exception as e:
        print(f"\nFailed to verify AWS credentials: {str(e)}")
        return False

def get_ecr_credentials():
    """Get ECR credentials using AWS CLI"""
    try:
        result = subprocess.run(
            ['aws', 'ecr', 'get-login-password'],
            capture_output=True,
            text=True,
            env=os.environ
        )
        if result.returncode != 0:
            raise Exception(f"Failed to get ECR credentials: {result.stderr}")
        return result.stdout.strip()
    except Exception as e:
        print(f"Failed to get ECR credentials: {str(e)}")
        raise

def login_to_ecr(password):
    """Login to ECR using Docker CLI"""
    try:
        cmd = f"echo {password} | docker login -u AWS --password-stdin {os.getenv('AWS_ACCOUNT_ID')}.dkr.ecr.{os.getenv('AWS_REGION')}.amazonaws.com"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to login to ECR: {result.stderr}")
        print("Successfully logged in to ECR")
    except Exception as e:
        print(f"Failed to login to ECR: {str(e)}")
        raise

def build_and_push_image():
    """Build and push the Docker image to ECR."""
    try:
        # Load environment variables and get config
        config = load_env_vars()
        
        # Verify AWS credentials
        verify_aws_credentials()
        
        # Get ECR credentials
        ecr_password = get_ecr_credentials()
        
        # Login to ECR
        login_to_ecr(ecr_password)
        
        # Build the Docker image
        print("Building Docker image...")
        subprocess.run([
            "docker", "build",
            "-t", f"{config.ecr_repo_name}:latest",
            "-f", "src/app/Dockerfile",
            "src/app"
        ], check=True)
        
        # Tag the image
        print("Tagging Docker image...")
        subprocess.run([
            "docker", "tag",
            f"{config.ecr_repo_name}:latest",
            f"{config.account_id}.dkr.ecr.{config.region}.amazonaws.com/{config.ecr_repo_name}:latest"
        ], check=True)
        
        # Push the image to ECR
        print("Pushing Docker image to ECR...")
        subprocess.run([
            "docker", "push",
            f"{config.account_id}.dkr.ecr.{config.region}.amazonaws.com/{config.ecr_repo_name}:latest"
        ], check=True)
        
        print("Successfully built and pushed Docker image to ECR")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building or pushing Docker image: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_and_push_image() 