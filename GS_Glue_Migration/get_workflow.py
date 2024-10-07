import boto3

glue_client = boto3.client("glue")


response = glue_client.get_workflow(
    Name='GSD-GlueWorkshop-WF',
    IncludeGraph=True
)

print(response)