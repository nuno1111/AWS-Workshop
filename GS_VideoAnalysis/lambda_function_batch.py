import upstage_ocr_endpoint
import s3_functions
import bedrock_functions

print('Loading function')

## 변수선언
config_name = "Upstage-Document-OCR-config"
endpoint_name = "endpoint-Upstage-Document-OCR"
bucket = "gsshop-video-analysis-761482380245-ap-northeast-2"
staging_prefix = "images/staging/"
# done_prefix = "images/done/"


def video_analyze(key):
  prefix = key.replace("_SUCCESS","")

  ### 2-4. s3에서 image 목록 불러오기
  keys = s3_functions.list_s3_keys(bucket, prefix)
  input_ocr_list = "<input_ocr_list>\n"

  ### 2-5 Upstage OCR 엔드포인트 호출
  print(f"Total keys found: {len(keys)}")
  
  i = 0
  for s3_key in keys:
      # print("s3_key ==> " + s3_key)
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
  
  ### 3-8 Json 결과 s3에 저장
  source_folder = prefix
  destination_folder = source_folder.replace("staging","done")
  s3_functions.move_s3_folder(bucket, source_folder, destination_folder)

def lambda_handler(event, context):

    # 3-1. _SUCCESS 파일 목록 찾기
    success_files = s3_functions.find_success_files(bucket, staging_prefix)
    print(f"Found {len(success_files)} '_SUCCESS' files:")
    
    # 3-2. success_files이 존재 하면 프로세싱
    if len(success_files) > 0:
      
      # 2-3. Endpoint 생성 및 배포
      upstage_ocr_endpoint.create_upstage_ocr_endpoint(
          endpoint_name=endpoint_name,
          config_name=config_name
      )

      for key in success_files:
        video_analyze(key)
      
      # 3-9 Upstage Endpoint 삭제
      upstage_ocr_endpoint.delete_upstage_ocr_endpoint(
          endpoint_name=endpoint_name
      )
      
    print(f"GS SHOP Video Analysis Seccess!!")

# lambda_handler(event=None,context=None)