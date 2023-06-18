# Account Name 기준으로 Bucket명 설정
AWS_ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
AWS_REGION=`aws configure get region`
BUCKET_NAME=immersion-day-${AWS_ACCOUNT_ID}

# data 폴더 업로드
aws s3 cp ./aws.png s3://${BUCKET_NAME}/ 

echo "aws.png 파일을 업로드하였습니다."
