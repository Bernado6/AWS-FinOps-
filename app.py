from aws_cdk import Tags
import aws_cdk as cdk

from sagemaker_stack.sagemaker_stack import SageMakerStack

app = cdk.App()
SagemakerResourcesManager = SageMakerStack(app, "SageMakerStack")

Tags.of(SagemakerResourcesManager).add("CreatedBy", "Bkipngeno")
Tags.of(SagemakerResourcesManager).add("Project", "Financial Operations")
Tags.of(SagemakerResourcesManager).add("Tribe", "Big Data and AI")
Tags.of(SagemakerResourcesManager).add("Owner", "Big Data")
Tags.of(SagemakerResourcesManager).add("Squad", "GenAI")
Tags.of(SagemakerResourcesManager).add("Name", "FinOps")


app.synth()
