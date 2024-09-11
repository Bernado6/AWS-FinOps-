import json
import boto3
import logging
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

print(logger.level)

def lambda_handler(event, context):
    endpoint_spec = json.loads(os.environ['ENDPOINT_SPEC'])
    tags = json.loads(os.environ['TAGS'])  # Assuming TAGS is a JSON array of tags in the environment variable

    logger.info("Endpoint spec: " + str(endpoint_spec))
    if not endpoint_spec:
        logger.error("Environment variable 'ENDPOINT_SPEC' not set")
        raise Exception("Environment variable 'ENDPOINT_SPEC' not set")
    if not isinstance(endpoint_spec, list):
        logger.error("Environment variable 'ENDPOINT_SPEC' must be an array")
        raise Exception("Environment variable 'ENDPOINT_SPEC' must be an array")
    for endpoint_spec_element in endpoint_spec:
        if not ('EndpointConfigName' in endpoint_spec_element and 'EndpointName' in endpoint_spec_element):
            logger.error("Environment variable 'ENDPOINT_SPEC' is in the wrong format")
            raise Exception("Environment variable 'ENDPOINT_SPEC' is in the wrong format")

    sm_client = boto3.client('sagemaker')
    anyFailed = False
    for endpoint_spec_element in endpoint_spec:
        endpoint_name = endpoint_spec_element['EndpointName']
        logger.info(f"Checking if SageMaker Endpoint exists: {endpoint_name}")

        # Check if the endpoint already exists
        try:
            sm_client.describe_endpoint(EndpointName=endpoint_name)
            logger.info(f"Endpoint {endpoint_name} already exists. Skipping creation.")
            continue  # Skip to the next endpoint
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                logger.info(f"Endpoint {endpoint_name} does not exist. Proceeding to create.")
            else:
                logger.error(f"Error checking endpoint {endpoint_name}: {e}")
                anyFailed = True
                continue  # Skip to the next endpoint if there's an unexpected error

        # Create the endpoint if it does not exist
        logger.info("Creating SageMaker Endpoint: " + endpoint_name)
        try:
            response = sm_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_spec_element['EndpointConfigName']
            )

            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                logger.error("Error creating endpoint: " + str(response))
                anyFailed = True
                continue  # Continue with the other endpoint creation
        except ClientError as e:
            logger.error(f"Error creating endpoint {endpoint_name}: {e}")
            anyFailed = True
            continue

        # Adding tags to the created endpoint
        if tags:
            logger.info(f"Adding tags to SageMaker Endpoint: {endpoint_name}")
            try:
                tag_response = sm_client.add_tags(
                    ResourceArn=response['EndpointArn'],
                    Tags=tags
                )
                if tag_response['ResponseMetadata']['HTTPStatusCode'] != 200:
                    logger.error(f"Error adding tags to endpoint: {endpoint_name} - {str(tag_response)}")
                    anyFailed = True
            except ClientError as e:
                logger.error(f"Error adding tags to endpoint {endpoint_name}: {e}")
                anyFailed = True

    if anyFailed:
        raise Exception("Error creating endpoint or adding tags")

    return {
        'statusCode': 200,
        'body': json.dumps('Created SageMaker Endpoint(s) successfully')
    }














# import json
# import boto3
# import logging
# import os

# logger = logging.getLogger()
# logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

# print(logger.level)

# def lambda_handler(event, context):
#     endpoint_spec = json.loads(os.environ['ENDPOINT_SPEC'])
#     logger.info("Endpoint spec: " + str(endpoint_spec))
#     if not endpoint_spec:
#         logger.error("Environment variable 'ENDPOINT_SPEC' not set")
#         raise Exception("Environment variable 'ENDPOINT_SPEC' not set")
#     # verify if endpoint_spec is an array
#     if not isinstance(endpoint_spec, list):
#         logger.error("Environment variable 'ENDPOINT_SPEC' must be an array")
#         raise Exception("Environment variable 'ENDPOINT_SPEC' must be an array")
#     # check if every element in the array has the required  keys
#     for endpoint_spec_element in endpoint_spec:
#         if not ('EndpointConfigName' in endpoint_spec_element and 'EndpointName' in endpoint_spec_element):
#             logger.error("Environment variable 'ENDPOINT_SPEC' is in the wrong format")
#             raise Exception("Environment variable 'ENDPOINT_SPEC' is in the wrong format")

#     sm_client = boto3.client('sagemaker')
#     anyFailed = False
#     for endpoint_spec_element in endpoint_spec:
#         logger.info("Creating SageMaker Endpoint: " + endpoint_spec_element['EndpointName'])
#         response = sm_client.create_endpoint(
#             EndpointName=endpoint_spec_element['EndpointName'],
#             EndpointConfigName=endpoint_spec_element['EndpointConfigName']
#         )
    
#         if response['ResponseMetadata']['HTTPStatusCode'] != 200:
#             logger.error("Error creating endpoint: " + str(response))
#             anyFailed = True
#             # continue with the other endpoint creation
            
#     if anyFailed:
#         raise Exception("Error creating endpoint")
        
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Created SageMaker Endpoint successfully')
#     }