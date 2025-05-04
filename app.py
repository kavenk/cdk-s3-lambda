#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_s3_lambda_stack import CdkS3LambdaStack

def main():
    """
    Main entry point for the CDK application.
    Creates and deploys the S3 Lambda processor stack.
    """
    app = cdk.App()
    
    # Deploy to the default AWS account and region from environment variables
    env = cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION")
    )
    
    # Create the stack instance
    CdkS3LambdaStack(app, "CdkS3LambdaStack", env=env)
    
    # Synthesize the CloudFormation template
    app.synth()

if __name__ == "__main__":
    main()
