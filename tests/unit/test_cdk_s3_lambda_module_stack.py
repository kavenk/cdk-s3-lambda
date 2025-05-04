import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_s3_lambda_module.cdk_s3_lambda_module_stack import CdkS3LambdaModuleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_s3_lambda_module/cdk_s3_lambda_module_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkS3LambdaModuleStack(app, "cdk-s3-lambda-module")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
