# Account Name 기준으로 Bucket명 설정
AWS_ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
# AWS_REGION=`aws configure get region`
AWS_REGION=$AWS_REGION
BUCKET_NAME=${AWS_ACCOUNT_ID}-iceberg-workshop-bucket
echo " "
# echo "export BUCKET_NAME=\"${BUCKET_NAME}\"" >> /home/ec2-user/.bashrc
# echo "export AWS_REGION=\"${AWS_REGION}\"" >> /home/ec2-user/.bashrc
# echo "export AWS_ACCOUNT_ID=\"${AWS_ACCOUNT_ID}\"" >> /home/ec2-user/.bashrc
echo ${AWS_ACCOUNT_ID}
echo ${BUCKET_NAME}
echo ${AWS_REGION}

# 버킷 생성
aws s3api create-bucket --bucket ${BUCKET_NAME} --region ${AWS_REGION}

# logs 폴더 생성
aws s3api put-object --bucket ${BUCKET_NAME} --key iceberg/
aws s3api put-object --bucket ${BUCKET_NAME} --key iceberg/flight_delays_iceberg/
aws s3api put-object --bucket ${BUCKET_NAME} --key query_results/

# database 생성
aws glue create-database \
  --database-input '{
    "Name": "iceberg",
    "Description": "Iceberg 데이터베이스입니다."
  }'

