import boto3
import json
import time

sagemaker_runtime = boto3.client("sagemaker-runtime")
sagemaker_client = boto3.client('sagemaker')

def create_upstage_ocr_endpoint(endpoint_name, config_name):
    print(f"Creating endpoint: '{endpoint_name}'")
    sagemaker_client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=config_name
    )
    
    # 엔드포인트 생성 완료 대기
    while True:
        response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        status = response['EndpointStatus']
        print(f"Endpoint status: {status}")
        if status == 'InService':
            break
        elif status == 'Failed':
            raise Exception(f"Endpoint creation failed for {endpoint_name}")
        time.sleep(10)
    
    print(f"Created endpoint: '{endpoint_name}'")

### 2-6. Upstage OCR Endpoint 호출
def invoke_endpoint(endpoint_name, image_data, content_type):
    """SageMaker 엔드포인트를 호출합니다."""
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType=content_type,
        Body=image_data
    )
    return json.loads(response["Body"].read().decode('utf-8'))

### 2-8 Upstage Endpoint 삭제
def delete_upstage_ocr_endpoint(endpoint_name):
    sagemaker_client.delete_endpoint(
        EndpointName=endpoint_name
    )
    print(f"Deleted endpoint: '{endpoint_name}'")
