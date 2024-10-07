import boto3

class GlueJobManager:
    def __init__(self, region_name):
        self.region_name = region_name
        self.glue_client = boto3.client('glue', region_name=region_name)

    def list_jobs(self):
        """
        AWS Glue에서 모든 작업(Job)을 조회합니다.
        """
        response = self.glue_client.list_jobs()
        jobs = response['JobNames']
        return jobs

    def get_job_details(self, job_name):
        """
        AWS Glue에서 특정 작업(Job)의 세부 정보를 조회합니다.
        """
        response = self.glue_client.get_job(JobName=job_name)
        job_details = response['Job']
        return job_details

# 사용 예시
glue_manager = GlueJobManager('us-east-1')  # 리전 이름을 입력하세요.

# 모든 작업(Job) 목록 조회
jobs = glue_manager.list_jobs()
print("AWS Glue Jobs:")
for job in jobs:
    print(job)

# 특정 작업(Job)의 세부 정보 조회
job_name = 'HiveNotebook'  # 작업 이름을 입력하세요.
job_details = glue_manager.get_job_details(job_name)
print(f"\nJob Details for {job_name}:")
print(job_details)
print(job_details['Name'])
print(job_details['JobMode'])
print(job_details['Role'])
print(job_details['Command'])
print(job_details['Command']['ScriptLocation'])