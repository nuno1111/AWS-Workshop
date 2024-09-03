import boto3
import json
import time
from botocore.exceptions import ClientError

region_name = "us-east-1" # Bedrock과 Sagemaker Region은 us-east-1으로 설정

sagemaker_runtime = boto3.client("sagemaker-runtime",region_name=region_name)
sagemaker_client = boto3.client("sagemaker",region_name=region_name)


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
    try:
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType=content_type,
            Body=image_data
        )
        return json.loads(response["Body"].read().decode('utf-8'))

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'ModelError' and '503' in error_message:
            return "ModelError 503"
        else:
            print(f"예상치 못한 오류 발생: {error_code} - {error_message}")
            raise  # 다른 종류의 오류면 바로 예외를 발생시킴

### 2-8 Upstage Endpoint 삭제
def delete_upstage_ocr_endpoint(endpoint_name):
    sagemaker_client.delete_endpoint(
        EndpointName=endpoint_name
    )
    print(f"Deleted endpoint: '{endpoint_name}'")
