# Account Name 기준으로 Bucket명 설정
AWS_ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
AWS_REGION=`aws configure get region`
BUCKET_NAME=sagemaker-immersion-day-${AWS_ACCOUNT_ID}

echo " "
echo "export BUCKET_NAME=\"${BUCKET_NAME}\"" >> /home/ec2-user/.bashrc
echo "export AWS_REGION=\"${AWS_REGION}\"" >> /home/ec2-user/.bashrc
echo "export AWS_ACCOUNT_ID=\"${AWS_ACCOUNT_ID}\"" >> /home/ec2-user/.bashrc
echo ${AWS_ACCOUNT_ID}
echo ${BUCKET_NAME}
echo ${AWS_REGION}

# 버킷 생성
aws s3api create-bucket --bucket ${BUCKET_NAME} --region ${AWS_REGION}

# data 폴더 업로드
aws s3 cp ./hotel_bookings.csv s3://${BUCKET_NAME}/dataset/
