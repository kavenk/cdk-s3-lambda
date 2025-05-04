
# Welcome to your CDK Python project!

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.


# CDK S3 Lambda Module

AWS CDK project that creates an S3 bucket and Lambda function that processes uploaded files.

## Local Setup and Testing

### Prerequisites

- AWS CLI
- Node.js (v14+)
- Python 3.12
- Git

### Quick Start

```bash
# Extract and cd to the repository

cd cdk-s3-lambda-module

# Alternatively you can clone it from 
git clone https://github.com/kavenk/cdk-s3-lambda.git

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, region (e.g., us-east-1), and output format (json)

# Install dependencies
npm install -g aws-cdk                     # Install CDK CLI
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip        # Update pip
pip install -r requirements.txt  # Install Python dependencies

# Deploy the stack
cdk bootstrap                              # Only needed first time in an AWS account/region
cdk deploy --require-approval never        # Deploy the stack

# Get the bucket name from the output
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name CdkS3LambdaStack --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" --output text)

# Test by uploading a file
echo '{"message": "Test file", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}' > sample.txt
aws s3 cp sample.txt s3://$BUCKET_NAME/sample.txt

# Check Lambda logs
LAMBDA_NAME=$(aws cloudformation describe-stacks --stack-name CdkS3LambdaStack --query "Stacks[0].Outputs[?OutputKey=='LambdaFunction'].OutputValue" --output text)
aws logs tail /aws/lambda/$LAMBDA_NAME --follow

# Destroy the stack when done
aws s3 rm s3://$BUCKET_NAME --recursive    # Empty bucket first
cdk destroy --force                        # Delete all resources
```

### Project Structure

- `cdk_s3_lambda_module/` - CDK infrastructure code
- `lambda/` - Lambda function code
- `tests/` - Unit tests

### Local Development 

1. Make changes to CDK stack in `cdk_s3_lambda_module/cdk_s3_lambda_module_stack.py`
2. Test with `cdk synth` to generate CloudFormation template
3. Deploy changes with `cdk deploy`

### Lambda Development

1. Edit Lambda function in `lambda/file_processor.py`
2. Test locally with sample events
3. Deploy with `cdk deploy`

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that:
1. Sets up the environment
2. Deploys the CDK stack
3. Tests the Lambda by uploading a file
4. Verifies the Lambda processed it correctly
5. Cleans up all resources



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!