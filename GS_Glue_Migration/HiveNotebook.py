## 다음은 Job 실행시에만 필요한 코드입니다.
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Notebook에선 아래 주석 풀고 사용
from awsglue.context import GlueContext
glueContext = GlueContext(spark)

# Define the table you want to read
table_name = "sample_07"
HiveJDBCConnector_node1703300245595 = glueContext.create_dynamic_frame.from_options(
    connection_type="custom.jdbc",
    connection_options={
        "tableName": table_name,
        "dbTable": table_name,
        "connectionName": "hive-jdbc-connection"
    },
    transformation_ctx="HiveJDBCConnector_node1703300245595",
)
HiveJDBCConnector_node1703300245595.show(5)
HiveJDBCConnector_node1703300245595.toDF().createOrReplaceTempView("sample_07")
spark.sql("""select * from sample_07""").show()
# Script generated for node Amazon S3
AmazonS3_node1703403476763 = glueContext.write_dynamic_frame.from_options(
    frame=HiveJDBCConnector_node1703300245595,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://emr-dev-exp-541948677097/HiveNotebookJob/sample_07/",
        "partitionKeys": [],
    },
    format_options={"compression": "snappy"},
    transformation_ctx="AmazonS3_node1703403476763",
)
%%chat
Write AWS Glue Script Code which get data from Amazon RDS and save to s3.

job.commit()