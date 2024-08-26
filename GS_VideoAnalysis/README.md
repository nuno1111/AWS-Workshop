## GS GSHOP Video Analysis 데모

### 00. 셋팅정보

- python library (Local 테스트 할 경우만 설치)

        pip install boto3 sagemaker setuptools

### 01. S3에 파일 업로드 & S3 Trigger 설정

- 참조 : https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/with-s3-example.html
- S3 버킷 생성
- S3 버킷에 images / results 폴더 생성

- Lambda용 Role & Policy 만들기

        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": [
                        "arn:aws:s3:::[S3버킷명]/*",
                        "arn:aws:s3:::[S3버킷명]"
                    ]
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:CreateLogGroup",
                        "logs:PutLogEvents"
                    ],
                    "Resource": [
                        "arn:aws:logs:*:*:*"
                    ]
                },
                {
                    "Sid": "VisualEditor2",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "sagemaker:CreateEndpoint",
                        "sagemaker:DescribeEndpoint",
                        "sagemaker:DeleteEndpoint"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": "sagemaker:InvokeEndpoint",
                    "Resource": "arn:aws:sagemaker:ap-northeast-2:[12자리-aws계정]:endpoint/endpoint-*"
                }
            ]
        }

- 테스트용 lambda 생성
- 타임아웃 15분 설정 : Configuration TAP > General configuration 

### 02. Upstage OCR 시작/중지 ( API / Batch )

- 참조 사이트 : https://aws.amazon.com/marketplace/pp/prodview-anvrh24vv3yiw
- 참조 노트북 : https://github.com/UpstageAI/cookbook/blob/main/cookbooks/upstage/aws/jumpstart/01_ocr.ipynb

- SageMaker Execution Role 필요
  - AmazonSageMakerFullAccess 정책추가
  - 아래 정책 추가

        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::*"
                    ]
                }
            ]
        }


- Upstage OCR Subcribe
  - Subscribe 진행 ( 참조사이트 확인 )
- SageMaker에서 모델 생성 ( main.ipynb 2-1 참조 )
  - SageMaker > Inference > Models
- SageMaker에서 Endpoint Config 설정 ( main.ipynb 2-2 참조 )
  - SageMaker > Inference > Endpoint configurations
  - Variants 에서 Instance type : ml.g5.2xlarge로 변경

### 03. Lambda에서 OCR 및 Bedrock 호출 
- lambda_function 소스 참고