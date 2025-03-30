#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.append('.')

from aws_cdk import App
from dotenv import load_dotenv

from src.scripts.platform_stack import PlatformStack
from src.utils.config import PlatformConfig

# Load environment variables.
load_dotenv()

# Create CDK app
app = App()

# Load configuration
config = PlatformConfig()

# Create the platform stack
PlatformStack(app, "PlatformStack", config)

app.synth() 