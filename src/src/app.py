#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.append('.')

import aws_cdk as cdk
from dotenv import load_dotenv

from src.stacks.platform_stack import PlatformStack
from src.utils.config import PlatformConfig

# Load environment variables.
load_dotenv()

# Create CDK app
app = cdk.App()

# Load configuration
config = PlatformConfig.from_env()

# Create the platform stack
PlatformStack(
    app,
    "PlatformStack",
    config=config,
    env=cdk.Environment(
        account=config.account_id,
        region=config.region
    ),
    description="Platform infrastructure stack for internal tools",
)

app.synth() 