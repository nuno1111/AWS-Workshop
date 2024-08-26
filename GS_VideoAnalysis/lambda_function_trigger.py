import urllib.parse

import utils
import upstage_ocr_endpoint
import s3_functions
import bedrock_functions

print('Loading function')

## 변수선언
config_name = "Upstage-Document-OCR-config"

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    prefix = key.replace("_SUCCESS","")
    print("bucket ==> ", bucket)
    print("key ==> ", key)
    print("prefix ==> ", prefix)
    
    # 2-3. Endpoint 생성 및 배포
    endpoint_name = utils.sanitize_endpoint_name(prefix)
    upstage_ocr_endpoint.create_upstage_ocr_endpoint(
        endpoint_name=endpoint_name,
        config_name=config_name
    )

    ### 2-4. s3에서 image 목록 불러오기
    keys = s3_functions.list_s3_keys(bucket, prefix)
    input_ocr_list = "<input_ocr_list>\n"

    ### 2-5 Upstage OCR 엔드포인트 호출
    print(f"Total keys found: {len(keys)}")
    
    i = 0
    for s3_key in keys:
        print("s3_key ==> " + s3_key)
        if prefix != s3_key and f"{prefix}_SUCCESS" != s3_key:
            image_data, content_type = s3_functions.download_from_s3(bucket, s3_key)
            # print("image_data ==> ",image_data)
            # print("content_type ==> ",content_type)

            # 엔드포인트 호출 (S3에서 가져온 Content-Type 사용)
            response = upstage_ocr_endpoint.invoke_endpoint(endpoint_name, image_data, content_type)
            
            original_ocr_text = response["text"]
            
            ## OCR만 적용
            input_ocr_list += "<frame>\n"
            input_ocr_list += "  <frame_id>{}</frame_id>\n".format(i)
            input_ocr_list += "  <original_ocr_text>{}</original_ocr_text>\n".format(original_ocr_text)
            # input_ocr_list += "  <croped_ocr_text>{}</croped_ocr_text>\n".format(croped_ocr_text)
            input_ocr_list += "</frame>\n"
            
            i = i+1
    input_ocr_list += "</input_ocr_list>"
    print(f"Upstage Call Ended")

    ### 2-6 bedrock 호출
    result_json = bedrock_functions.get_final_result(input_ocr_list)

    ### 2-7 Json 결과 s3에 저장
    split_result = prefix.split("/")
    result_path_key = f"results/{split_result[3]}.json"
    s3_functions.save_result_json(bucket, result_path_key, result_json)
    
    ### 2-8 Upstage Endpoint 삭제
    upstage_ocr_endpoint.delete_upstage_ocr_endpoint(
        endpoint_name=endpoint_name
    )
    
    print(f"GS SHOP Video Analysis Seccess!!")

event = {
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "1970-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "gsshop-video-analysis-761482380245-ap-northeast-2",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::gsshop-video-analysis-761482380245-ap-northeast-2"
        },
        "object": {
          "key": "images/prd_01/vrid_00003/_SUCCESS",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
}    
lambda_handler(event,context=None)