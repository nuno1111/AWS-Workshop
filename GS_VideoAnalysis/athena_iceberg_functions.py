import boto3
import time

# Athena 클라이언트 생성
athena_client = boto3.client('athena')
s3_output = "s3://gsshop-video-analysis-761482380245-ap-northeast-2/logs/athena_output/"
database_name = "video_analysis"
table_name = "video_analysis_logs"


def run_query(query):
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database_name},
        ResultConfiguration={'OutputLocation': s3_output}
    )
    query_execution_id = response['QueryExecutionId']

    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = response['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            return state, response
        time.sleep(1)

# Create (Insert)
def insert_data(vrid, current_time, batch_execution_time, status, error_message, partition_date):
    query = f"""
    INSERT INTO {table_name}
    VALUES (
        '{vrid}',
        TIMESTAMP '{current_time}',
        {batch_execution_time},
        '{status}',
        '{error_message}',
        DATE '{partition_date}'
    )
    """
    state, _ = run_query(query)
    print(f"Insert operation {state}")

# Read
def read_data(partition_date):
    query = f"""
    SELECT *
    FROM {table_name}
    WHERE partition_date = DATE '{partition_date}'
    """
    state, response = run_query(query)
    if state == 'SUCCEEDED':
        result_response = athena_client.get_query_results(
            QueryExecutionId=response['QueryExecution']['QueryExecutionId']
        )
        # Process and return the results
        return result_response['ResultSet']['Rows']
    else:
        print(f"Read operation {state}")
        return None

# Update
# def update_data(vrid, new_status, partition_date):
#     query = f"""
#     UPDATE {table_name}
#     SET status = '{new_status}'
#     WHERE vrid = '{vrid}' AND partition_date = DATE '{partition_date}'
#     """
#     state, _ = run_query(query)
#     print(f"Update operation {state}")

# # Delete
# def delete_data(vrid, partition_date):
#     query = f"""
#     DELETE FROM {table_name}
#     WHERE vrid = '{vrid}' AND partition_date = DATE '{partition_date}'
#     """
#     state, _ = run_query(query)
#     print(f"Delete operation {state}")

