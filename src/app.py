#!/usr/bin/env python3
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aws_cdk import App, Environment
from scripts.platform_stack import PlatformStack
from scripts.config import PlatformConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create CDK app
app = App()

# Load configuration
config = PlatformConfig()

# Create the platform stack with environment
env = Environment(
    account=config.account_id,
    region=config.region
)

PlatformStack(app, "PlatformStack", config, env=env)

app.synth() 