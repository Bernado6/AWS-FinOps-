from constructs import Construct
from aws_cdk import (
    Duration, 
    App, 
    Stack,
    CfnOutput,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    Tags
    
)


class SageMakerStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Parameters
        # Sagemaker endpoints to be excluded
        endpoint_exclude_tag_key = self.node.try_get_context("endpoint_exclude_tag_key") or "env"
        endpoint_exclude_tag_value = self.node.try_get_context("endpoint_exclude_tag_value") or "prod"
        # Sagemaker notebooks to be excluded
        notebook_exclude_tag_key = self.node.try_get_context("notebook_exclude_tag_key") or "env"
        notebook_exclude_tag_value = self.node.try_get_context("notebook_exclude_tag_value") or "prod"
        
        environment_variables={
                "ENDPOINT_EXCLUDE_TAG": '{"Key": "' + endpoint_exclude_tag_key + '", "Value": "' + endpoint_exclude_tag_value + '"}',
            "NOTEBOOK_EXCLUDE_TAG": '{"Key": "' + notebook_exclude_tag_key + '", "Value": "' + notebook_exclude_tag_value + '"}',
            "MAX_COUNT": "100",
            "LOG_LEVEL": "INFO"
            }
        
        
        # create lambda image for on demand index creation
        existing_role_arn = 'arn:aws:iam::690288626781:role/Sagemaker-Endpoint-Creation-Role'
        existing_sagemaker_endpoint_creation_role = iam.Role.from_role_arn(
            self,
            "ExistingSagemakerEndpointCreationRole",
            existing_role_arn)
        
        
        # Lambda function to clean SageMaker resources
        clean_function = lambda_.DockerImageFunction(
            self, 
            "Clean-SageMaker-Resources-Function-CFN",
            function_name="Clean-SageMaker-Resources-fn",
            code=lambda_.DockerImageCode.from_image_asset("sagemaker-clean-docker-image"),
            role=existing_sagemaker_endpoint_creation_role,
            memory_size=10240,
            timeout=Duration.minutes(10),
            environment=environment_variables 
        )

        # Lambda function to create SageMaker endpoints
         # {"EndpointConfigName": "HuggingFace-llama-2-13b",
         # "EndpointName": "HuggingFace-llama-2-13b"},
        # , {"EndpointConfigName": "Streaming-HR-App-Endpoint","EndpointName": "Streaming-HR-App-Endpoint"}
        ENDPOINT_SPEC = '[{"EndpointConfigName": "HR-App-Endpint","EndpointName": "HR-App-Endpint"}, {"EndpointConfigName": "Financial-llama-config-no-autoscaling","EndpointName": "Financial-Llama-Model-Endpoint"}, {"EndpointConfigName": "Service-Management-Chatbot-Endpoint","EndpointName": "Service-Management-Chatbot-Endpoint"}, {"EndpointConfigName": "Zuri-Endpoint","EndpointName": "Zuri-Endpoint"},{"EndpointConfigName": "Bedrock-HR-App-Endpoint","EndpointName": "Bedrock-HR-App-Endpoint"}]'
        
        TAGS = '[{"Key": "Project", "Value": "GenAI"}, {"Key": "CreatedBy", "Value": "GenAI"}, {"Key": "Owner", "Value": "GenAI"}, {"Key": "Environment", "Value": "UAT"}]'

        
        environment_variable = {
                "ENDPOINT_SPEC": ENDPOINT_SPEC,  
                "MAX_COUNT": "100",
                "TAGS": TAGS
            }
        
        create_function = lambda_.DockerImageFunction(
            self, 
            "Create-SageMaker-Endpoint-Function-CFN",
            function_name="Create-SageMaker-Endpoint-fn",
            code=lambda_.DockerImageCode.from_image_asset("sagemaker-create-docker-image"),
            role=existing_sagemaker_endpoint_creation_role,
            memory_size=10240,
            timeout=Duration.minutes(10),
            environment=environment_variable 
        )
        
        
        # Schedule events for the clean Lambda function
        
        clean_sagemaker_resource_rule = events.Rule(
            self, 
            "Clean-SageMaker-Resources-Function-Schedule",
            schedule=events.Schedule.cron(hour="16", minute="0")
        )
        ## Add the Lambda clean function as a target for the 7:00 PM rule
        clean_sagemaker_resource_rule.add_target(targets.LambdaFunction(clean_function))
        
        # Schedule events for the create Lambda function
        create_sagemaker_resource_rule = events.Rule(
            self, 
            "Create-SageMaker-Endpoint-Function-Schedule",
            schedule=events.Schedule.cron(hour="04", minute="0", week_day="MON-FRI")
        )
        
        ## Add the Lambda create function as a target for the 6:00 AM rule
        create_sagemaker_resource_rule.add_target(targets.LambdaFunction(create_function))
        
        Tags.of(clean_sagemaker_resource_rule).add("CreatedBy", "Bkipngeno")
        Tags.of(clean_sagemaker_resource_rule).add("Project", "Financial Operations")
        Tags.of(clean_sagemaker_resource_rule).add("Tribe", "Big Data and AI")
        Tags.of(clean_sagemaker_resource_rule).add("Owner", "Big Data")
        Tags.of(clean_sagemaker_resource_rule).add("Squad", "GenAI")
        Tags.of(clean_sagemaker_resource_rule).add("Name", "FinOps")
# #         # Apply tags to your Lambda function
#         Tags.of(create_function).add("CreatedBy", "Bkipngeno")
#         Tags.of(create_function).add("Project", "Financial Operations")
#         Tags.of(create_function).add("Tribe", "Big Data and AI")
#         Tags.of(create_function).add("Owner", "Big Data")
#         Tags.of(create_function).add("Squad", "GenAI")
#         Tags.of(create_function).add("Name", "FinOps")

#         # Optionally, you can apply the same tags to the EventBridge rule
#         # Apply tags to your Lambda function
        Tags.of(create_sagemaker_resource_rule).add("CreatedBy", "Bkipngeno")
        Tags.of(create_sagemaker_resource_rule).add("Project", "Financial Operations")
        Tags.of(create_sagemaker_resource_rule).add("Tribe", "Big Data and AI")
        Tags.of(create_sagemaker_resource_rule).add("Owner", "Big Data")
        Tags.of(create_sagemaker_resource_rule).add("Squad", "GenAI")
        Tags.of(create_sagemaker_resource_rule).add("Name", "FinOps")
        
        # Outputs
        CfnOutput(
            self, "Clean-SageMaker-Resources-Function",
            description="Clean SageMaker Resources Lambda Function ARN",
            value=clean_function.function_arn
        )

        CfnOutput(
            self, "existing_sagemaker_endpoint_creation_role",
            description="Implicit IAM Role created for lambda function",
            value=clean_function.role.role_arn
        )
