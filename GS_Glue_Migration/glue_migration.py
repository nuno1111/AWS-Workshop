import boto3
from botocore.exceptions import ClientError

# A 계정 설정
# a_region_name = "us-west-2"
# a_access_key = "YOUR_A_ACCOUNT_ACCESS_KEY"
# a_secret_key = "YOUR_A_ACCOUNT_SECRET_KEY"
# a_glue_client = boto3.client("glue", region_name=a_region_name, aws_access_key_id=a_access_key, aws_secret_access_key=a_secret_key)
# a_s3_client = boto3.client("s3", region_name=a_region_name, aws_access_key_id=a_access_key, aws_secret_access_key=a_secret_key)

a_region_name = "us-east-1"
a_glue_client = boto3.client("glue", region_name=a_region_name)
a_s3_client = boto3.client("s3", region_name=a_region_name)

# B 계정 설정
# b_region_name = "us-east-1"
# b_access_key = "YOUR_B_ACCOUNT_ACCESS_KEY"
# b_secret_key = "YOUR_B_ACCOUNT_SECRET_KEY"
# b_glue_client = boto3.client("glue", region_name=b_region_name, aws_access_key_id=b_access_key, aws_secret_access_key=b_secret_key)
# b_s3_client = boto3.client("s3", region_name=b_region_name, aws_access_key_id=b_access_key, aws_secret_access_key=b_secret_key)

b_region_name = "us-east-1"
b_glue_client = boto3.client("glue", region_name=b_region_name)
b_s3_client = boto3.client("s3", region_name=b_region_name)

# Glue Job 이름
job_name = "HiveNotebook"

# A 계정에서 Glue Job 스크립트 다운로드
try:
    job_response = a_glue_client.get_job(JobName=job_name)
    job_script_location = job_response["Job"]["Command"]["ScriptLocation"]
    job_role = job_response["Job"]["Role"]
    job_commnand_name = job_response["Job"]["Command"]["Name"]
    job_mode = job_response["Job"]["JobMode"]

    print(f"A 계정의 Glue Job '{job_name}' 스크립트 위치: {job_script_location}")
    print(job_response)
    # 스크립트 다운로드
    script_file = job_script_location.split("/")[-1]
    a_s3_client.download_file(
        Bucket=job_script_location.split("/")[2],
        Key="/".join(job_script_location.split("/")[3:]),
        Filename=script_file
    )
    print(f"스크립트 '{script_file}' 다운로드 완료")

except ClientError as e:
    print(f"A 계정의 Glue Job '{job_name}' 가져오기 실패: {e}")

# B 계정에서 필요한 리소스 생성
# ... IAM 역할, Glue 데이터 카탈로그 데이터베이스, 연결 등 생성 코드 ...

# print(boto3.__version__)


upload_script_location = f"s3://aws-glue-assets-541948677097-us-east-1/scripts/HiveNotebook2.py"
b_job_name = "H_HiveNotebook"
b_job_role = job_role
b_commnand_name = job_commnand_name
# b_job_mode = job_mode
b_job_mode = "NOTEBOOK"

# B 계정에 Glue Job 스크립트 업로드
try:
    # upload_script_location = f"s3://<script-bucket>/<script-path>/{script_file}"
    b_s3_client.upload_file(
        Filename=script_file,
        Bucket=upload_script_location.split("/")[2],
        Key="/".join(upload_script_location.split("/")[3:])
    )
    print(f"스크립트 '{script_file}' 업로드 완료")
    print(b_job_mode)
    # B 계정에 Glue Job 생성
    b_glue_client.create_job(
        Name=b_job_name,
        JobMode='NOTEBOOK',
        Role=b_job_role,
        Command={
            "Name": b_commnand_name,
            "ScriptLocation": upload_script_location,
            "PythonVersion": '3'
        },
        WorkerType='G.1X', 
        NumberOfWorkers=5, 
        GlueVersion='4.0'
    )
    
    # b_glue_client.update_job(
    #     JobName='H_HiveNotebook',
    #     JobUpdate={
    #         'JobMode': 'NOTEBOOK',
    #         'Role': 'arn:aws:iam::541948677097:role/AWSGlueServiceRole-glueworkshop', 
    #         'Command': {'Name': 'glueetl', 'ScriptLocation': 's3://aws-glue-assets-541948677097-us-east-1/scripts/HiveNotebook2.py', 'PythonVersion': '3'}, 
    #     }
    # )
    print(f"B 계정에 Glue Job '{b_job_name}' 생성 완료")

except ClientError as e:
    print(f"B 계정에 Glue Job '{b_job_name}' 생성 실패: {e}")
    
"""
{
'Name': 'HiveNotebook', 
'JobMode': 'NOTEBOOK', 
'Description': '', 
'Role': 'arn:aws:iam::541948677097:role/AWSGlueServiceRole-glueworkshop', 
'CreatedOn': datetime.datetime(2023, 12, 23, 11, 59, 46, 708000, tzinfo=tzlocal()), 
'LastModifiedOn': datetime.datetime(2023, 12, 28, 10, 23, 9, 542000, tzinfo=tzlocal()), 
'ExecutionProperty': {'MaxConcurrentRuns': 1}, 
'Command': {'Name': 'glueetl', 'ScriptLocation': 's3://aws-glue-assets-541948677097-us-east-1/scripts/HiveNotebook.py', 'PythonVersion': '3'}, 
'DefaultArguments': {'--enable-job-insights': 'false', '--job-language': 'python', '--TempDir': 's3://aws-glue-assets-541948677097-us-east-1/temporary/', '--enable-glue-datacatalog': 'true', 'library-set': 'analytics'}, 
'Connections': {'Connections': ['hive-jdbc-connection']}, 
'MaxRetries': 0, 
'AllocatedCapacity': 5, 
'Timeout': 2880, 
'MaxCapacity': 5.0, 
'WorkerType': 'G.1X', 
'NumberOfWorkers': 5, 
'GlueVersion': '4.0', 
'ExecutionClass': 'STANDARD'
}
"""