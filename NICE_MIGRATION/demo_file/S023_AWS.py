import airflow  
from airflow import DAG  

from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

from datetime import timedelta, date, datetime

# 운영환경
# yyyymm = '{{(execution_date.replace(day=1)-macros.timedelta(days=1)).strftime("%Y%m")}}'
# YYYY = '{{(execution_date.replace(day=1)-macros.timedelta(days=1)).strftime("%Y")}}'
# MM = '{{(execution_date.replace(day=1)-macros.timedelta(days=1)).strftime("%m")}}'

# 테스트환경
yyyymm = '202507'
YYYY = '2025'
MM = '07'
S3_BUCKET_NAME = "demo.nice.co.kr.datalake"

# 기본 설정 정보 정의
default_args = {
    'owner': 'ghkim',
    'depends_on_past': True,
    'start_date': datetime(2025,3,20),
    'provide_context':True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

# DAG 선언
dag = DAG(
    'S023',
    default_args=default_args,
    description='S023',
    schedule_interval= None
)

s3_sensor = S3KeySensor(
    task_id='s3_sensor',
    bucket_name=S3_BUCKET_NAME,
    bucket_key="DI/CARD/KB_MEDI/ORG/" + YYYY + "/" + MM + "/_SUCCESS",
    dag=dag
)

S023_getraw_task = GlueJobOperator(
    task_id="S023-getraw-task",
    job_name="S023-getraw",
    script_args={
        '--yyyymm': yyyymm
    },
    dag=dag
)

S023_dataprocessing_task = GlueJobOperator(
    task_id="S023-dataprocessing-task",
    job_name="S023-dataprocessing",
    script_args={
        '--yyyymm': yyyymm
    },
    dag=dag
)


s3_sensor >> S023_getraw_task >> S023_dataprocessing_task
# S023_getraw_task >> S023_dataprocessing_task