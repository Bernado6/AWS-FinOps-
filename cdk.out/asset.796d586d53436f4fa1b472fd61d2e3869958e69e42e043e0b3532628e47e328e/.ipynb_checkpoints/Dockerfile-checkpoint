# FROM public.ecr.aws/lambda/python:3.8
FROM public.ecr.aws/lambda/python:3.10
# FROM public.ecr.aws/lambda/python:3.9

COPY sagemaker_create_requirements.txt  .
RUN  pip3 install -r sagemaker_create_requirements.txt --target "${LAMBDA_TASK_ROOT}"
 
# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}
 
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "sagemaker_create.lambda_handler" ]

# Set cache to a location lambda can write to
ENV TRANSFORMERS_CACHE="/tmp/TRANSFORMERS_CACHE"