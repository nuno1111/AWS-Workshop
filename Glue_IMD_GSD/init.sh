# Account Name 기준으로 Bucket명 설정
AWS_ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
AWS_REGION=`aws configure get region`
BUCKET_NAME=${AWS_ACCOUNT_ID}-analytics-workshop-bucket
echo " "
echo "export BUCKET_NAME=\"${BUCKET_NAME}\"" >> /home/ec2-user/.bashrc
echo "export AWS_REGION=\"${AWS_REGION}\"" >> /home/ec2-user/.bashrc
echo "export AWS_ACCOUNT_ID=\"${AWS_ACCOUNT_ID}\"" >> /home/ec2-user/.bashrc
echo ${BUCKET_NAME}
echo ${AWS_ACCOUNT_ID}

# 버킷 생성
aws s3api create-bucket --bucket ${BUCKET_NAME} --region ${AWS_REGION}

# data 폴더 업로드
aws s3 cp data/ s3://${BUCKET_NAME}/data/ --recursive

# jupyter job을 위한 policy 생성
aws iam create-policy --policy-name AWSGlueInteractiveSessionPassRolePolicy --policy-document '{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Action": "iam:PassRole","Resource":"arn:aws:iam::'${AWS_ACCOUNT_ID}':role/Analyticsworkshop-GlueISRole"}]}'

# GlueWorkshop Role 생성
aws iam create-role --role-name Analyticsworkshop-GlueISRole --assume-role-policy-document '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Principal": { "Service": "glue.amazonaws.com" }, "Action": "sts:AssumeRole" } ] }'
aws iam attach-role-policy --role-name Analyticsworkshop-GlueISRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole
aws iam attach-role-policy --role-name Analyticsworkshop-GlueISRole --policy-arn arn:aws:iam::aws:policy/service-role/AwsGlueSessionUserRestrictedNotebookPolicy
aws iam attach-role-policy --role-name Analyticsworkshop-GlueISRole --policy-arn arn:aws:iam::aws:policy/AWSGlueInteractiveSessionPassRolePolicy
aws iam attach-role-policy --role-name Analyticsworkshop-GlueISRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

