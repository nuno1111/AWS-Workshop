from os import path
from datetime import timedelta  
import airflow  
from airflow import DAG  
from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator,
    EmrCreateJobFlowOperator,
    EmrTerminateJobFlowOperator,
)
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

S3_BUCKET_NAME = "airflow-617700b0-a7a7-11ee-bce1-0a2692f872c9-bucket"
GLUE_ROLE_ARN = "arn:aws:iam::264014135458:role/AWSGlueServiceRoleDefault"

dag_name = 'data-pipeline'
# Unique identifier for the DAG
correlation_id = "{{ run_id }}"
  
default_args = {  
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1),
    'retries': 0,
    'retry_delay': timedelta(minutes=2),
    'provide_context': True,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False
}

dag = DAG(  
    dag_name,
    default_args=default_args,
    dagrun_timeout=timedelta(hours=2),
    schedule_interval='0 3 * * *'
)

s3_sensor = S3KeySensor(  
  task_id='s3_sensor',  
  bucket_name=S3_BUCKET_NAME,  
  bucket_key='data/raw/green*', 
  wildcard_match=True, 
  dag=dag  
)

glue_crawler_config = {
        "Name": "airflow-workshop-raw-green-crawler",
        "Role": GLUE_ROLE_ARN,
        "DatabaseName": "default",
        "Targets": {"S3Targets": [{"Path": f"{S3_BUCKET_NAME}/data/raw/green"}]},
    }
    
glue_crawler = GlueCrawlerOperator(
    task_id="glue_crawler",
    config=glue_crawler_config,
    dag=dag)

glue_job = GlueJobOperator(
    task_id="glue_job",
    job_name="nyc_raw_to_transform",
    script_location=f"s3://{S3_BUCKET_NAME}/scripts/glue/nyc_raw_to_transform.py",
    s3_bucket=S3_BUCKET_NAME,
    iam_role_name="AWSGlueServiceRoleDefault",
    create_job_kwargs={"GlueVersion": "4.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    script_args={'--dag_name': dag_name,
                 '--task_id': 'glue_task',
                 '--correlation_id': correlation_id},
    dag=dag  
)


## Override values for task Id 'create_emr_cluster'
JOB_FLOW_OVERRIDES = {
    "Name": dag_name + ".create_emr_cluster-" + correlation_id,
    "ReleaseLabel": "emr-6.13.0",
    "LogUri": "s3://{}/logs/emr/{}/create_emr_cluster/{}".format(S3_BUCKET_NAME, dag_name, correlation_id), 
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Leader node",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m7g.xlarge",
                "InstanceCount": 1
            },
            {
                "Name": "Core nodes",
                "Market": "ON_DEMAND",
                "InstanceRole": "CORE",
                "InstanceType": "m7g.xlarge",
                "InstanceCount": 2
            }
        ],
        "TerminationProtected": False,
        "KeepJobFlowAliveWhenNoSteps": True
    },
    "Tags": [ 
      { 
         "Key": "correlation_id",
         "Value": correlation_id
      },
      { 
         "Key": "dag_name",
         "Value": dag_name
      }
   ]
}

S3_URI = "s3://{}/scripts/emr/".format(S3_BUCKET_NAME)  

## Steps for task Id 'add_steps'
SPARK_TEST_STEPS = [
  {
      'Name': 'setup - copy files',
      'ActionOnFailure': 'CANCEL_AND_WAIT',
      'HadoopJarStep': {
          'Jar': 'command-runner.jar',
          'Args': ['aws', 's3', 'cp', '--recursive', S3_URI, '/home/hadoop/']
      }
  },
  {
      'Name': 'Run Spark',
      'ActionOnFailure': 'CANCEL_AND_WAIT',
      'HadoopJarStep': {
          'Jar': 'command-runner.jar',
          'Args': ['spark-submit',
                   '/home/hadoop/nyc_aggregations.py',
                   's3://{}/data/transformed/green'.format(S3_BUCKET_NAME),
                   's3://{}/data/aggregated/green'.format(S3_BUCKET_NAME),
                    dag_name,
                    'add_steps',
                    correlation_id]
      }
  }
]

cluster_creator = EmrCreateJobFlowOperator(
    task_id='create_emr_cluster',
    job_flow_overrides=JOB_FLOW_OVERRIDES,
    aws_conn_id='aws_default',
    emr_conn_id='emr_default',
    dag=dag
)

step_adder = EmrAddStepsOperator(
    task_id='add_steps',
    job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=SPARK_TEST_STEPS,
    dag=dag
)

step_checker1 = EmrStepSensor(
    task_id='watch_step1',
    job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('add_steps', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

step_checker2 = EmrStepSensor(
    task_id='watch_step2',
    job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull('add_steps', key='return_value')[1] }}",
    aws_conn_id='aws_default',
    dag=dag
)

cluster_remover = EmrTerminateJobFlowOperator(
    task_id='remove_cluster',
    job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

copy_to_redshift = S3ToRedshiftOperator(
    task_id='copy_to_redshift',
    schema='nyc',
    table='green',
    s3_bucket=S3_BUCKET_NAME,
    s3_key='data/aggregated',
    copy_options=["FORMAT AS PARQUET"],
    dag=dag,
)

s3_sensor >> glue_crawler >> glue_job >> cluster_creator >> step_adder >> step_checker1 >> step_checker2 >> cluster_remover >> copy_to_redshift
