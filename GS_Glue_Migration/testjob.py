import boto3

glue_client = boto3.client("glue")

job_name = 'test_glue_job'
job_mode = 'NOTEBOOK'
job_role = 'arn:aws:iam::541948677097:role/AWSGlueServiceRole-glueworkshop'
upload_script_location = "s3://aws-glue-assets-541948677097-us-east-1/scripts/HiveNotebook2.py"
# upload_script_location = "s3://aws-glue-assets-541948677097-us-east-1/notebooks/HiveNotebook.ipynb"
glue_client.delete_job(
    JobName=job_name
)
print("delete job")
glue_client.create_job(
    Name=job_name,
    JobMode=job_mode,
    Role=job_role,
    Command={
        "Name": 'glueetl',
        "ScriptLocation": upload_script_location,
        # "PythonVersion": '3'
    },
    # WorkerType='G.1X', 
    # NumberOfWorkers=5, 
    # GlueVersion='4.0'
)
print("create job")

