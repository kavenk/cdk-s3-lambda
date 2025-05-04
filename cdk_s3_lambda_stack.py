from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    RemovalPolicy,
    Duration,
    CfnOutput,
)
from constructs import Construct

class CdkS3LambdaStack(Stack):
    """
    CDK Stack that creates:
    - An S3 bucket for file processing
    - A Lambda function to process files uploaded to the bucket
    - S3 event notifications to trigger the Lambda
    - Security policies for the bucket and Lambda
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """
        Initialize the stack with all required AWS resources.
        
        Args:
            scope: The parent construct
            construct_id: The ID of this stack
            **kwargs: Additional parameters passed to the Stack constructor
        """
        super().__init__(scope, construct_id, **kwargs)

        # Define user-friendly names with prefixes to avoid global naming conflicts
        # Use lowercase for S3 bucket names as they must be DNS compliant
        bucket_name = "kaushik-pmv-assignment-bucket-" + self.account + "-" + self.region
        lambda_name = "FileProcessorFunction"

        # Create an S3 bucket for storing files to be processed
        bucket = s3.Bucket(
            self, "ProcessingBucket",
            bucket_name=bucket_name,  # Specify a custom bucket name
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # Create the Lambda function that will process uploaded files
        file_processor = lambda_.Function(
            self, "FileProcessor",
            function_name=lambda_name,  # Specify a custom function name
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="file_processor.handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        # Grant the Lambda function read permissions on the S3 bucket
        bucket.grant_read(file_processor)

        # Configure S3 event notifications to trigger the Lambda when files are created
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(file_processor),
            s3.NotificationKeyFilter(suffix=".txt")
        )

        # Create a bucket policy to enforce HTTPS connections only
        bucket_policy = iam.PolicyStatement(
            effect=iam.Effect.DENY,
            actions=["s3:*"],
            resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"],
            principals=[iam.AnyPrincipal()],
            conditions={
                "Bool": {"aws:SecureTransport": "false"}
            }
        )
        
        # Apply the policy to the bucket
        bucket.add_to_resource_policy(bucket_policy)

        # Output the resource names for easy reference after deployment
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
        CfnOutput(self, "LambdaFunction", value=file_processor.function_name)
