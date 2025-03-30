from setuptools import setup, find_packages

setup(
    name="platform-infrastructure",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aws-cdk-lib>=2.130.0",
        "constructs>=10.0.0",
        "python-dotenv>=1.0.1",
        "boto3>=1.34.51",
        "botocore>=1.34.51",
    ],
) 