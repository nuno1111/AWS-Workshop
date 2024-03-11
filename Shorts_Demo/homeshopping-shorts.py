import boto3
import time
import json
from urllib.parse import urlparse

# boto3 Timeout 셋팅
from botocore.config import Config

config = Config(
    read_timeout=900,
    connect_timeout=900,
    retries={"max_attempts": 0}
)

# AWS 기본정보
BucketName = "[동영상-저장되어있는-버킷명]"
transcribe_client = boto3.client('transcribe', region_name = 'us-east-1')
bedrock_client = boto3.client('bedrock-runtime', region_name = 'us-east-1', config=config)
s3_client = boto3.client('s3')

# llm_model = 'anthropic.claude-v2:1'
llm_model = 'anthropic.claude-instant-v1'

# 01. AWS Transcribe 수행
def transcribe_job(job_name, file_name):
    
    try: 
        transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
        )
        # transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        # print(job_name + " Deleted")
        print(job_name + " exist!")

    except Exception as e:
        print("A job doesn't exist:", e)
    
        file_uri = "s3://" + BucketName + '/input/' + file_name
        outputKey='output/'+job_name

        transcribe_client.start_transcription_job(
            TranscriptionJobName = job_name,
            Media = {
                'MediaFileUri': file_uri
            },
            MediaFormat = file_name.split('.')[1],
            LanguageCode = 'ko-KR',
            # LanguageCode = 'en-US',
            Subtitles={
                'Formats': [
                    'vtt','srt'
                ],
                'OutputStartIndex': 0
            },
            OutputBucketName=BucketName,
            OutputKey=outputKey
        )

        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            job = transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
            job_status = job['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                print(f"Job {job_name} is {job_status}.")
                if job_status == 'COMPLETED':
                    print(
                        f"Download the transcript from\n"
                        f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                break
            else:
                print(f"Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)
        
        print("01. AWS Transcribe 수행 성공") 

# 02. Transcribe vtt 받아오기
def extract_s3_info_from_url(s3_url):
    # URL을 파싱하여 객체 생성
    parsed_url = urlparse(s3_url)

    # S3 URL 형식인지 확인
    if parsed_url.scheme == 'https' and parsed_url.netloc.startswith('s3.'):
        # netloc에서 's3.' 부분을 제거하고 나머지를 '/'로 분리하여 버킷 이름과 객체 키 추출
        s3_components = parsed_url.path.split('/', 2)
        bucket_name = s3_components[1]
        object_key = s3_components[2] if len(s3_components) > 2 else ''

        return bucket_name, object_key
    else:
        raise ValueError("주어진 URL은 올바른 S3 URL 형식이 아닙니다.")
    
def get_transcribe_vtt(job_name):
    # transcribe_client = boto3.client('transcribe', region_name = 'us-east-1')

    job = transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
    vtt_location = job['TranscriptionJob']['Subtitles']['SubtitleFileUris'][1]

    # 주어진 URL에서 버킷 이름과 객체 키 추출
    bucket_name, object_key = extract_s3_info_from_url(vtt_location)

    # 추출된 정보 출력
    # print("Bucket 이름:", bucket_name)
    # print("Object 키:", object_key)

    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    text_data = response['Body'].read().decode('utf-8')

    # 텍스트 데이터 처리 예제 (이 예제에서는 간단히 텍스트를 출력)
    return text_data

# 02-1. input vtt를 json으로 변환
def vtt_to_json(vtt_file, duration_param):
    data = []
    lines = vtt_file.splitlines()

    # print(lines)
    # Skip the first line (WEBVTT)
    lines = lines[1:]
    
    idx = 0
    while idx < len(lines):
        if re.match(r'^\d+$', lines[idx].strip()):
            entry = {}
            idx += 1
            
            # Extract time stamps
            timing = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})', lines[idx])
            start_time = f"{timing.group(1)}:{timing.group(2)}:{timing.group(3)}.{timing.group(4)}"
            end_time = f"{timing.group(5)}:{timing.group(6)}:{timing.group(7)}.{timing.group(8)}"
            entry['start_time'] = start_time
            entry['end_time'] = end_time
            idx += 1
            
            # Extract text
            text = ''
            while idx < len(lines) and lines[idx].strip() != '':
                text += lines[idx].strip() + ' '
                idx += 1
            entry['text'] = text.strip()
            
            # Calculate duration
            start_hour, start_minute, start_second, start_millisecond = map(int, timing.group(1, 2, 3, 4))
            end_hour, end_minute, end_second, end_millisecond = map(int, timing.group(5, 6, 7, 8))
            start_total = (start_hour * 3600 + start_minute * 60 + start_second) * 1000 + start_millisecond
            end_total = (end_hour * 3600 + end_minute * 60 + end_second) * 1000 + end_millisecond
            duration = end_total - start_total
            entry['duration'] = duration / 1000  # Convert to seconds
            
            if duration > duration_param:                
                data.append(entry)
            
        else:
            idx += 1
                
    return data

# 02-2-1. Bedrock을 사용하여 평가결과 받아오기
def get_evaluation(product_category, subtitle):

    prompt_data = """
다음 """ + product_category + """ 방송 자막을 평가하세요. 평가는 0.0부터 100.0까지의 점수로 표기해주세요.

- 자막이 """ + product_category + """ 관련 된 경우:

이 자막은 혼쇼핑 제작의 어려움, 해외 현지 촬영 등 에피소드를 이해 하는데 기여합니다.
이 자막이 홈쇼핑 제작의 상품에 대한 설명이나 에피소드에 관련된 내용이면 높은 점수를 부여합니다.

- 방송 자막 : <subtitle>"""+subtitle+"""</subtitle>

결과는 다음과 같이 <score>태그에 평가점수만 알려주세요.
- 앞뒤 설명하는 문구는 반드시 제외되고, 평가결과 즉, score만 알려주세요.
- 결과 예시 : <score>[0.0 ~ 100.0]</score>
"""    
    
    # Claude Prompt
    body = json.dumps({
        "prompt": f"\n\nHuman:{prompt_data}\n\nAssistant:",
        "max_tokens_to_sample": 4096,
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]            
        }) 

    modelId = llm_model
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock_client.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    # print(response_body)
    score_lines = response_body.get("completion")
    
    # score에서 점수 가져오기
    pattern = r'<score>(.*?)</score>'
    score = 0.0
    for line in score_lines.splitlines():
        match = re.search(pattern, line)
        if match:
            score = float(match.group(1))
    print(subtitle + " : score : " + str(score))
    return score

# 02-2. input json 에 LLM으로 점수 받아오기
def get_score_from_llm(input_json, product_category):
    validated_json = []
    for i in range(len(input_json)):
        text = input_json[i]['text']
        # 점수 받아오기
        score = get_evaluation(product_category, text)
        input_json[i]['score'] = score
        validated_json.append(input_json[i])
    return validated_json    

# 02-4. 1분 이상 만 추출하기
def get_one_min_json(sorted_json, seconds):
    one_min_json = []
    sum_duration = 0.0
    for i in range(len(sorted_json)):    
        sum_duration += sorted_json[i]['duration']
        one_min_json.append(sorted_json[i])
        if sum_duration >= seconds:
            break            
    return one_min_json

# 04. create_summarized_video
import re
def extract_time_ranges(sorted_one_min_json):
    time_ranges = []

    for i in range(len(sorted_one_min_json)):
        start_time = sorted_one_min_json[i]['start_time']
        end_time = sorted_one_min_json[i]['end_time']
        time_ranges.append((start_time, end_time))
    
    # # 정규표현식을 사용하여 WEBVTT 형식에서 시간 정보를 추출합니다.
    # pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})')
    # matches = pattern.findall(webvtt_content)

    # # 추출된 매치를 리스트에 추가합니다.
    # for match in matches:
    #     start_time, end_time = match
    #     time_ranges.append((start_time, end_time))

    return time_ranges

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips

def cut_video(input_video_path, start_time, end_time):
    clip = VideoFileClip(input_video_path)
    subclip = clip.subclip(start_time, end_time)
    return subclip

def concatenate_videos(video_clips, output_video_path):
    final_clip = concatenate_videoclips(video_clips)
    final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
     
def create_summarized_video(file_name, sorted_one_min_json ):

    # save file to local pc from s3
    input_video_path = './input_'+file_name
    output_video_path = './output_'+file_name

    s3_client.download_file(BucketName, 'input/'+file_name, input_video_path)
    
    extracted_time_ranges = extract_time_ranges(sorted_one_min_json)

    # print(extracted_time_ranges)
    
    clips = []

     # 순서대로 입력된 시간 범위에 따라 동영상을 자르고 clips 리스트에 추가합니다.
    for start_time, end_time in extracted_time_ranges:
        clip = cut_video(input_video_path, start_time, end_time)
        clips.append(clip)

    concatenate_videos(clips, output_video_path)    

# 05. image_resize
import moviepy.editor as mp
from datetime import datetime
import PIL 
import os
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS 

def image_resize(input_video_path, output_shortform_path, one_min_json, video_title ):

    video = VideoFileClip(input_video_path)
    _w, _h = video.size
    # print(_w,_h)

    # video = video.crop(
    #     x1=int(_w * 0.1),
    #     x2=int(-1 * _w * 0.3),
    #     y2=int(-1 * _h * 0.1),
    # )
    _w, _h = video.size

    # print(_w,_h)

    hd_video = video.resize(width=1080) # 1920 X 1080 해상도로 크기 변경
    duration = hd_video.duration 

    w, h = hd_video.size
    # print(duration)
    # print(h)

    blank_clip = mp.ColorClip((w,1920), color=(0,0,0), duration=duration)    
    text_clip_top = mp.TextClip(video_title, fontsize=50, color='white', font='NanumGothic', align='center', size=(w,200)).set_pos(("center", 1920/2 - int(h/2) - 200 )).set_duration(duration)

    clips = [blank_clip, hd_video.set_pos(("center","center")), text_clip_top]
    
    # 하위 자막 추가
    start = 0.0
    end = 0.0
   
    for line in one_min_json:
        start_time = line['start_time']
        end_time = line['end_time']
        text = line['text']
        
        start_str = datetime.strptime(start_time, "%H:%M:%S.%f")
        end_str = datetime.strptime(end_time, "%H:%M:%S.%f")

        diff = end_str - start_str
        
        total_seconds = diff.total_seconds() 
        
        start = end
        end = end + total_seconds

        textclip = mp.TextClip(text, fontsize=40, color='white', font='NanumGothic', align='center', size=(w,200)).set_pos(("center", 1920/2 + int(h/2)))
        textclip = textclip.set_start(start).set_end(end)

        clips.append(textclip)

    final = mp.CompositeVideoClip(clips).set_duration(duration)

    final.write_videofile(output_shortform_path, codec="libx264", audio_codec="aac")

def main_job(job_name, file_name, product_category):
    
    print(job_name + " Start!!!!")
    
    # 01. AWS Transcribe 수행
    print("01.Transcribe_job Start!!!!")
    transcribe_job(job_name, file_name)

    # 02. Transcribe vtt 받아오기
    print("02. Transcribe vtt 받아오기 Start!!!!")
    input_vtt = get_transcribe_vtt(job_name)
    
    # 02-1. input vtt를 json으로 변환 / 2.5초 이상 자막만 받아오기
    input_json = vtt_to_json(input_vtt, 2500)    
    print(len(input_json))
    
    # 02-2. input json 에 LLM으로 점수 받아오기
    validated_json = get_score_from_llm(input_json, product_category)    
    
    # 02-3. index추가 후 점수로 정렬
    for i, item in enumerate(validated_json):
        validated_json[i]["index"] = i
    
    sorted_json = sorted(validated_json, key=lambda x: x['score'], reverse=True)
    # print(sorted_json)
   
    # 02-4. 1분 이상 만 추출하기
    one_min_json = get_one_min_json(sorted_json, 60)    
    # print(one_min_json)

    sorted_one_min_json = sorted(one_min_json, key=lambda x: x['index'], reverse=False)
    # print(sorted_one_min_json)
    
    # 04. create_summarized_video
    print("04. create_summarized_video Start!!!!")
    create_summarized_video(file_name, sorted_one_min_json)
    
    # 05. image_resize
    image_resize("./output_"+file_name, "./shortpic_v2_"+file_name, sorted_one_min_json, product_category )    
    s3_client.put_object(Body=open("./shortpic_v2_"+file_name, 'rb'), Bucket=BucketName, Key="output/shortpic_"+file_name)
    
    # 06. Delete Temp files
    os.remove("./input_"+file_name)
    os.remove("./output_"+file_name)
    # os.remove("./shortpic_"+file_name)
    
    print(job_name + " End!!!!")

if __name__ == "__main__":    
    print("Short pic Start!!!")
    
    # for file_name in FILE_LIST:    
    #     s3_filename = file_name[:9] + file_name[-4:]
    #     product_category = file_name[10:-7]
    #     main_job(s3_filename,product_category)
    # print("Short pic End!!!")
    
    main_job("[Transcribe_job_name]", "[동영상파일명]", "[상품카테고리&상품명]")
