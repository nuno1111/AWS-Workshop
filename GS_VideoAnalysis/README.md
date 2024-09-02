## GS GSHOP Video Analysis 데모

### 00. 셋팅정보

- python library (Local 테스트 할 경우만 설치)

        pip install boto3

- Lambda용 Role & Policy 만들기

        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "logs:CreateLogStream",
                        "s3:ListBucket",
                        "s3:DeleteObject",
                        "logs:CreateLogGroup",
                        "logs:PutLogEvents",
                        "s3:GetBucketLocation"
                    ],
                    "Resource": [
                        "arn:aws:s3:::gsshop-video-analysis-761482380245-ap-northeast-2",
                        "arn:aws:s3:::gsshop-video-analysis-761482380245-ap-northeast-2/*",
                        "arn:aws:logs:*:*:*"
                    ]
                },
                {
                    "Sid": "VisualEditor1",
                    "Effect": "Allow",
                    "Action": [
                        "athena:StartQueryExecution",
                        "sagemaker:CreateEndpoint",
                        "sagemaker:DeleteEndpoint",
                        "bedrock:InvokeModel",
                        "athena:GetQueryExecution",
                        "athena:GetQueryResults",
                        "sagemaker:DescribeEndpoint",
                        "sagemaker:InvokeEndpoint",
                        "glue:GetTable",
                        "glue:GetPartitions",
                        "glue:UpdateTable"
                    ],
                    "Resource": "*"
                }
            ]
        }

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

- Bedrock에서 모델 Access Grant 확인 (us-east-1)
  - 메뉴 : Amazon Bedrock Bedrock configurations > Model access
  - Access granted 확인


### 01. Upstage OCR 시작/중지 (us-east-1)

- 참조 사이트 : https://aws.amazon.com/marketplace/pp/prodview-anvrh24vv3yiw
- 참조 노트북 : https://github.com/UpstageAI/cookbook/blob/main/cookbooks/upstage/aws/jumpstart/01_ocr.ipynb

- Upstage OCR Subcribe
  - Subscribe 진행 ( 참조사이트 확인 )
  - 메뉴 : SageMaker > Inference > My marketplace model packages > TAB:AWS Marketplace subscriptions
- SageMaker에서 모델 생성 ( main.ipynb 2-1 참조 )
  - 메뉴 : SageMaker > Inference > Models
- SageMaker에서 Endpoint Config 설정 ( main.ipynb 2-2 참조 )
  - 메뉴 : SageMaker > Inference > Endpoint configurations
  

### 02. S3 설정 ( seoul region / ap-northeast-2 )

- S3 버킷 생성
- S3 버킷에 images / results / logs 폴더 생성
- iceberg를 위한 폴더 생성
  - logs/tables/
  - logs/athena_output/


- S3 trigger 사용시 참조 : https://docs.aws.amazon.com/ko_kr/lambda/latest/dg/with-s3-example.html 

### 03. Lambda ( seoul region / ap-northeast-2 ) 에서 OCR 및 Bedrock 호출 (us-east-1)
- lambda_layer 설정 (python 3.12 기준)
  - Layer 참조 : https://api.klayers.cloud/api/v2/p3.12/layers/latest/ap-northeast-2/html
  - Pillow 패키지 레이어 : arn:aws:lambda:ap-northeast-2:770693421928:layer:Klayers-p312-pillow:1
- 타임아웃 15분 설정 : Configuration TAP > General configuration 
- lambda_function_batch 소스 참고