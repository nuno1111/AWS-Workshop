import boto3
s3 = boto3.client('s3')

### 2-4. s3에서 image 목록 불러오기
def list_s3_keys(bucket_name, prefix):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    keys = []
    if 'Contents' in response:
        keys = [obj['Key'] for obj in response['Contents']]
    
    return keys

### 2-5. s3에서 image 다운로드
def download_from_s3(bucket, key):
    """S3에서 파일을 다운로드하고 바이너리 데이터와 Content-Type을 반환합니다."""
    response = s3.get_object(Bucket=bucket, Key=key)
    content_type = response['ContentType']
    data = response['Body'].read()
    return data, content_type

### 2-8. s3에서 결과 저장
def save_result_json(bucket, result_path_key, result_json):
    s3.put_object(
        Bucket=bucket,
        Key=result_path_key,
        Body=result_json,
        ContentType='application/json'
    )

### 2-8. s3에서 결과 저장
def find_success_files(bucket, prefix):
    # S3 클라이언트 생성
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    
    success_files = []
    if 'Contents' in response:
        for obj in response['Contents']:
            # 파일 이름이 '_SUCCESS'로 끝나는지 확인
            if obj['Key'].endswith('_SUCCESS'):
                success_files.append(obj['Key'])

    return success_files

### 2-9. 분석 후 폴더 이동
def move_s3_folder(bucket, source_folder, destination_folder):

    # 소스 폴더의 모든 객체 나열
    response = s3.list_objects_v2(Bucket=bucket, Prefix=source_folder)

    # 'Contents' 키가 응답에 있는지 확인
    if 'Contents' not in response:
        print(f"No objects found in {source_folder}")
        return

    for obj in response['Contents']:
        old_key = obj['Key']
        new_key = old_key.replace(source_folder, destination_folder, 1)

        # 객체 복사
        s3.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': old_key},
            Key=new_key
        )

        # 원본 객체 삭제
        s3.delete_object(Bucket=bucket, Key=old_key)

        print(f"Moved {old_key} to {new_key}")