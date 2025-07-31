#!/bin/zsh

# AWS Bedrock Claude 모델 CLI 호출 스크립트
# AWS CLI를 사용하여 각 Claude 모델을 순차적으로 호출

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본 설정
DEFAULT_PROMPT="인공지능과 머신러닝에 대해 매우 상세하고 포괄적으로 설명해주세요. 다음 내용들을 모두 포함하여 가능한 한 길고 자세하게 작성해주세요:

1. 인공지능의 역사적 발전 과정을 1950년대부터 현재까지 시대순으로 설명하고, 각 시대별 주요 연구자, 기술적 돌파구, 한계점을 상세히 기술해주세요.

2. 머신러닝의 주요 알고리즘들을 분류별로 설명해주세요:
- 지도학습: 선형회귀, 로지스틱회귀, 의사결정트리, 랜덤포레스트, SVM, 나이브베이즈 등
- 비지도학습: K-means, 계층적 클러스터링, DBSCAN, PCA, t-SNE 등
- 강화학습: Q-learning, 정책 그래디언트, Actor-Critic 등
각 알고리즘의 수학적 원리, 장단점, 적용 사례를 구체적으로 설명해주세요.

3. 딥러닝과 신경망에 대해 다음을 포함하여 설명해주세요:
- 퍼셉트론부터 다층 신경망까지의 발전 과정
- 역전파 알고리즘의 수학적 원리와 구현 방법
- CNN, RNN, LSTM, GRU, Transformer 등 각 아키텍처의 구조와 특징
- 활성화 함수, 손실 함수, 최적화 알고리즘들의 종류와 특성
- 배치 정규화, 드롭아웃, 정규화 기법들

4. 자연어 처리 분야의 발전 과정과 주요 기술들:
- 전통적인 NLP 기법부터 현대의 트랜스포머 기반 모델까지
- Word2Vec, GloVe, FastText 등 단어 임베딩 기법
- BERT, GPT, T5 등 사전 훈련된 언어 모델들의 구조와 특징
- 기계 번역, 질의응답, 텍스트 요약, 감정 분석 등 응용 분야

5. 컴퓨터 비전 분야의 주요 기술들:
- 이미지 전처리, 특징 추출, 객체 검출, 이미지 분할
- CNN의 발전 과정: LeNet, AlexNet, VGG, ResNet, DenseNet 등
- YOLO, R-CNN 계열 모델들의 객체 검출 기법
- GAN, VAE 등 생성 모델들의 원리와 응용

6. 실제 산업 적용 사례들을 구체적으로 설명해주세요:
- 의료 분야: 의료 영상 분석, 신약 개발, 진단 보조 시스템
- 금융 분야: 신용 평가, 알고리즘 트레이딩, 사기 탐지
- 자율주행: 센서 융합, 경로 계획, 장애물 인식
- 추천 시스템: 협업 필터링, 콘텐츠 기반 필터링, 하이브리드 방식
- 음성 인식과 합성: 스마트 스피커, 음성 어시스턴트

7. AI 개발 도구와 프레임워크들:
- TensorFlow, PyTorch, Keras, Scikit-learn 등의 특징과 사용법
- 클라우드 AI 서비스: AWS SageMaker, Google AI Platform, Azure ML
- MLOps와 모델 배포, 모니터링, 버전 관리

8. AI의 윤리적 고려사항과 미래 전망:
- 편향성, 공정성, 투명성, 설명 가능성
- AI의 사회적 영향과 일자리 변화
- AGI(Artificial General Intelligence)로의 발전 가능성

각 주제에 대해 구체적인 수식, 코드 예제, 실제 데이터셋 사례를 포함하여 매우 상세하게 설명해주세요. 초보자도 이해할 수 있도록 단계별로 설명하되, 전문적인 내용도 빠뜨리지 말고 포함해주세요. 

중요: 가능한 한 길고 자세하게 작성해주세요. 각 섹션마다 최소 2000단어 이상으로 작성하고, 모든 세부사항을 포함해주세요. 짧게 요약하지 말고, 예제와 설명을 풍부하게 포함하여 매우 포괄적으로 작성해주세요. 더 많은 내용을 포함할수록 좋습니다. 절대로 간단히 끝내지 말고, 계속해서 더 많은 정보와 예제를 제공해주세요."

# 모델별 토큰 가격 (USD per 1K tokens) - 2025년 1월 기준
typeset -A INPUT_TOKEN_PRICES
INPUT_TOKEN_PRICES[claude-3-haiku]="0.00025"
INPUT_TOKEN_PRICES[claude-3.5-sonnet-v2]="0.003"
INPUT_TOKEN_PRICES[claude-3.7-sonnet]="0.003"
INPUT_TOKEN_PRICES[claude-sonnet-4]="0.003"

typeset -A OUTPUT_TOKEN_PRICES
OUTPUT_TOKEN_PRICES[claude-3-haiku]="0.00125"
OUTPUT_TOKEN_PRICES[claude-3.5-sonnet-v2]="0.015"
OUTPUT_TOKEN_PRICES[claude-3.7-sonnet]="0.015"
OUTPUT_TOKEN_PRICES[claude-sonnet-4]="0.015"

# $1 이상 비용을 위한 모델별 프롬프트 생성
generate_high_cost_prompt() {
    local model_name="$1"
    local base_prompt=""
    
    case "$model_name" in
        "claude-3-haiku")
            base_prompt="다음 주제들에 대해 각각 매우 상세하고 포괄적인 설명을 작성해주세요. 각 주제마다 최소 20000단어 이상으로 작성하고, 구체적인 예시, 코드 샘플, 실제 사례를 포함해주세요. 절대로 짧게 요약하지 말고, 가능한 한 길고 자세하게 작성해주세요. 모든 세부사항을 포함하여 매우 포괄적으로 작성해주세요:

1. 머신러닝과 딥러닝의 차이점과 각각의 알고리즘들
2. 클라우드 컴퓨팅 아키텍처와 AWS 서비스들의 상세 분석
3. 웹 개발 프레임워크 비교 (React, Vue, Angular, Next.js 등)
4. 데이터베이스 설계 원칙과 SQL/NoSQL 비교
5. 사이버 보안 위협과 대응 방안

각 주제에 대해 초보자도 이해할 수 있도록 단계별로 설명하고, 실무에서 활용할 수 있는 팁과 베스트 프랙티스를 포함해주세요."
            ;;
        "claude-3.5-sonnet-v2"|"claude-3.7-sonnet"|"claude-sonnet-4")
            base_prompt="다음 주제들에 대해 매우 상세하고 전문적인 분석을 작성해주세요. 각 주제마다 최소 15000단어 이상으로 작성하고, 가능한 한 길고 자세하게 설명해주세요. 절대로 짧게 요약하지 말고, 모든 세부사항을 포함해서 작성해주세요. 매우 포괄적이고 길게 작성해주세요:

1. 현대 소프트웨어 아키텍처의 진화와 마이크로서비스 패턴
2. 클라우드 네이티브 애플리케이션 개발과 컨테이너 오케스트레이션
3. 머신러닝 모델의 프로덕션 배포와 MLOps
4. 분산 시스템 설계와 CAP 정리
5. 보안 중심 개발(Security by Design)과 제로 트러스트 아키텍처

각 주제에 대해 실제 구현 예시, 상세한 코드 샘플, 아키텍처 다이어그램 설명, 장단점 분석, 실무 적용 사례를 포함하여 매우 포괄적이고 길게 설명해주세요."
            ;;
    esac
    
    echo "$base_prompt"
}

# 테스트할 AWS 리전 목록
REGIONS=(
    "ap-northeast-2"  # Seoul
    "us-east-1"       # N. Virginia
    "us-west-2"       # Oregon
)

# Claude 모델 정의 (on-demand 모델)
CLAUDE_MODEL_NAMES=(
    "claude-3-haiku"
    "claude-3.5-sonnet-v2"
    "claude-3.7-sonnet"
    "claude-sonnet-4"
)

# 모델 이름으로 모델 ID 가져오는 함수 (리전별)
get_model_id() {
    local model_name="$1"
    local region="$2"
    local prefix=""
    
    # 리전에 따른 prefix 결정
    if [[ "$region" == ap-* ]]; then
        prefix="apac"
    elif [[ "$region" == us-* ]]; then
        prefix="us"
    else
        prefix="apac"  # 기본값
    fi
    
    case "$model_name" in
        "claude-3-haiku") echo "${prefix}.anthropic.claude-3-haiku-20240307-v1:0" ;;
        "claude-3.5-sonnet-v2") echo "${prefix}.anthropic.claude-3-5-sonnet-20241022-v2:0" ;;
        "claude-3.7-sonnet") echo "${prefix}.anthropic.claude-3-7-sonnet-20250219-v1:0" ;;
        "claude-sonnet-4") echo "${prefix}.anthropic.claude-sonnet-4-20250514-v1:0" ;;
        *) echo "" ;;
    esac
}

# 사용법 출력
usage() {
    echo "사용법: bedrock_claude_awscli_fixed.sh [옵션]"
    echo ""
    echo "옵션:"
    echo "  -p, --prompt TEXT     Claude 모델에게 보낼 프롬프트 (기본값: 자기소개 요청)"
    echo "  -m, --model MODEL     특정 모델만 테스트 (claude-3-haiku, claude-3.5-sonnet-v2, claude-3.7-sonnet, claude-sonnet-4)"
    echo "  -r, --region REGION   특정 리전만 테스트 (ap-northeast-2, us-east-1, us-west-2)"
    echo "  --all-models          모든 Claude 모델 테스트"
    echo "  --all-regions         모든 리전 테스트"
    echo "  --high-cost           \$1+ 비용 테스트 모드"
    echo "  --repeat-until-dollar \$1 달성까지 반복 호출 (무제한 시도)"
    echo "  -h, --help           이 도움말 출력"
    echo ""
    echo "예제:"
    echo "  ./bedrock_claude_awscli_fixed.sh -m claude-3-haiku -r ap-northeast-2"
    echo "  ./bedrock_claude_awscli_fixed.sh --all-models --all-regions"
    echo "  ./bedrock_claude_awscli_fixed.sh --repeat-until-dollar -m claude-3-haiku -r ap-northeast-2"
}

# 모델별 최대 토큰 수 결정
get_max_tokens() {
    local model_name="$1"
    local use_high_cost="${2:-false}"
    
    if [[ "$use_high_cost" == "true" ]]; then
        case "$model_name" in
            "claude-3-haiku") echo "100000" ;;
            "claude-3.5-sonnet-v2"|"claude-3.7-sonnet"|"claude-sonnet-4") echo "20000" ;;
            *) echo "20000" ;;
        esac
    else
        # 기본 토큰 수를 매우 크게 늘려서 더 많은 비용 발생
        case "$model_name" in
            "claude-3-haiku") echo "200000" ;;  # haiku는 저렴하므로 최대한 많은 토큰
            "claude-3.5-sonnet-v2"|"claude-3.7-sonnet"|"claude-sonnet-4") echo "100000" ;;  # sonnet도 많은 토큰으로 설정
            *) echo "100000" ;;
        esac
    fi
}

# 비용 계산 함수
calculate_cost() {
    local model_name="$1"
    local input_tokens="$2"
    local output_tokens="$3"
    
    if [[ "$input_tokens" == "N/A" || "$output_tokens" == "N/A" ]]; then
        echo "N/A"
        return
    fi
    
    local input_price="${INPUT_TOKEN_PRICES[$model_name]}"
    local output_price="${OUTPUT_TOKEN_PRICES[$model_name]}"
    
    if [[ -z "$input_price" || -z "$output_price" ]]; then
        echo "N/A"
        return
    fi
    
    # awk 사용 (macOS 호환성)
    local input_cost=$(awk "BEGIN {printf \"%.6f\", $input_tokens * $input_price / 1000}")
    local output_cost=$(awk "BEGIN {printf \"%.6f\", $output_tokens * $output_price / 1000}")
    local total_cost=$(awk "BEGIN {printf \"%.6f\", $input_cost + $output_cost}")
    
    echo "$total_cost"
}

# JSON 페이로드 생성 함수
create_payload() {
    local prompt="$1"
    local model_name="$2"
    local use_high_cost="${3:-false}"
    local max_tokens=$(get_max_tokens "$model_name" "$use_high_cost")
    
    jq -n \
        --arg prompt "$prompt" \
        --argjson max_tokens "$max_tokens" \
        '{
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": $max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": $prompt
                }
            ]
        }'
}

# Function to repeatedly call until $1 cost is achieved (unlimited attempts)
invoke_claude_model_until_dollar() {
    local model_name="$1"
    local model_id="$2"
    local prompt="$3"
    local region="$4"
    local use_high_cost="${5:-false}"
    local attempt=1
    local total_cost=0
    local total_input_tokens=0
    local total_output_tokens=0
    local max_attempts=1000  # 충분히 큰 수로 설정 (실질적으로 무제한)
    
    echo -e "${BLUE}🎯 $model_name 모델 - \$1 달성까지 반복 호출 (무제한 시도)${NC}"
    echo -e "${YELLOW}🌍 리전: $region${NC}"
    echo "================================================================================"
    
    while [[ $attempt -le $max_attempts ]]; do
        echo -e "${BLUE}📞 시도 ${attempt}/${max_attempts} - 현재 누적 비용: \$$(printf "%.6f" $total_cost)${NC}"
        
        # 고비용 테스트인 경우 특별한 프롬프트 사용
        local current_prompt="$prompt"
        if [[ "$use_high_cost" == "true" ]]; then
            current_prompt=$(generate_high_cost_prompt "$model_name")
            echo -e "${YELLOW}💰 고비용 테스트 모드 활성화${NC}"
        fi
        
        # 임시 파일 생성
        local payload_file=$(mktemp)
        local response_file=$(mktemp)
        local error_file=$(mktemp)
        
        # JSON 페이로드 생성
        create_payload "$current_prompt" "$model_name" "$use_high_cost" > "$payload_file"
        
        # AWS CLI로 Bedrock 호출
        local encoded_payload=$(base64 -i "$payload_file")
        
        echo -e "${BLUE}⏳ API 호출 중...${NC}"
        local start_time=$(date +%s)
        
        if aws bedrock-runtime invoke-model \
            --model-id "$model_id" \
            --body "$encoded_payload" \
            --content-type "application/json" \
            --region "$region" \
            "$response_file" 2>"$error_file"; then
            
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            echo -e "${GREEN}✅ 성공! (소요시간: ${duration}초)${NC}"
            
            # 응답 파싱
            local content=$(jq -r '.content[0].text' "$response_file" 2>/dev/null || echo "응답 파싱 실패")
            local input_tokens=$(jq -r '.usage.input_tokens // "N/A"' "$response_file" 2>/dev/null)
            local output_tokens=$(jq -r '.usage.output_tokens // "N/A"' "$response_file" 2>/dev/null)
            
            if [[ "$input_tokens" != "N/A" && "$output_tokens" != "N/A" ]]; then
                total_input_tokens=$((total_input_tokens + input_tokens))
                total_output_tokens=$((total_output_tokens + output_tokens))
                
                # 이번 호출 비용 계산
                local current_cost=$(calculate_cost "$model_name" "$input_tokens" "$output_tokens")
                if [[ "$current_cost" != "N/A" ]]; then
                    total_cost=$(awk "BEGIN {printf \"%.6f\", $total_cost + $current_cost}")
                    
                    echo -e "${YELLOW}📊 이번 호출:${NC}"
                    echo -e "   입력 토큰: ${input_tokens}"
                    echo -e "   출력 토큰: ${output_tokens}"
                    echo -e "   이번 비용: \$${current_cost} USD"
                    
                    echo -e "${YELLOW}📈 누적 통계:${NC}"
                    echo -e "   총 입력 토큰: ${total_input_tokens}"
                    echo -e "   총 출력 토큰: ${total_output_tokens}"
                    echo -e "   총 누적 비용: \$$(printf "%.6f" $total_cost) USD"
                    
                    # $1 목표 달성 확인
                    local cost_check=$(awk "BEGIN {print ($total_cost >= 1.0) ? 1 : 0}")
                    if [[ "$cost_check" == "1" ]]; then
                        echo -e "${GREEN}🎉 \$1+ 비용 목표 달성! (총 ${attempt}회 호출)${NC}"
                        echo -e "${GREEN}💬 마지막 응답 미리보기:${NC}"
                        echo "$content" | head -c 500
                        if [ ${#content} -gt 500 ]; then
                            echo "..."
                        fi
                        echo ""
                        
                        # 임시 파일 정리
                        rm -f "$payload_file" "$response_file" "$error_file"
                        return 0
                    else
                        echo -e "${YELLOW}⚠️  아직 \$1 미달성 (현재: \$$(printf "%.6f" $total_cost)) - 계속 시도 중...${NC}"
                        
                        # 10회 이상 시도했을 때 추가 메시지
                        if [[ $attempt -ge 10 ]]; then
                            echo -e "${BLUE}ℹ️  10회 이상 시도 중... 목표 달성까지 계속 진행합니다.${NC}"
                        fi
                    fi
                fi
            fi
            
        else
            echo -e "${RED}❌ 실패: 모델 호출 중 오류 발생${NC}"
            if [ -f "$error_file" ] && [ -s "$error_file" ]; then
                echo -e "${RED}오류 내용:${NC}"
                cat "$error_file"
            fi
            
            # 연속 실패 시 대기 시간 증가
            local wait_time=5
            if [[ $attempt -ge 5 ]]; then
                wait_time=10
            elif [[ $attempt -ge 10 ]]; then
                wait_time=15
            fi
            
            echo -e "${YELLOW}⏳ ${wait_time}초 대기 후 재시도...${NC}"
            sleep $wait_time
        fi
        
        # 임시 파일 정리
        rm -f "$payload_file" "$response_file" "$error_file"
        
        attempt=$((attempt + 1))
        echo -e "${NC}----------------------------------------${NC}"
        
        # 성공한 호출 후 잠시 대기 (API 레이트 리밋 방지)
        if [[ $attempt -le $max_attempts ]]; then
            sleep 3
        fi
    done
    
    # 이 부분은 실질적으로 도달하지 않음 (max_attempts=1000)
    echo -e "${RED}❌ 예상치 못한 종료 - \$1 목표 미달성${NC}"
    echo -e "${YELLOW}📈 최종 누적 통계:${NC}"
    echo -e "   총 입력 토큰: ${total_input_tokens}"
    echo -e "   총 출력 토큰: ${total_output_tokens}"
    echo -e "   총 누적 비용: \$$(printf "%.6f" $total_cost) USD"
    return 1
}

# General Claude model invocation function
invoke_claude_model() {
    local model_name="$1"
    local model_id="$2"
    local prompt="$3"
    local region="$4"
    local use_high_cost="${5:-false}"
    
    echo -e "${BLUE}🤖 $model_name 모델 호출 중...${NC}"
    
    # 고비용 테스트인 경우 특별한 프롬프트 사용
    if [[ "$use_high_cost" == "true" ]]; then
        prompt=$(generate_high_cost_prompt "$model_name")
        echo -e "${YELLOW}💰 고비용 테스트 모드 활성화${NC}"
    fi
    
    # 임시 파일 생성
    local payload_file=$(mktemp)
    local response_file=$(mktemp)
    local error_file=$(mktemp)
    
    # JSON 페이로드 생성
    create_payload "$prompt" "$model_name" "$use_high_cost" > "$payload_file"
    
    # AWS CLI로 Bedrock 호출
    local encoded_payload=$(base64 -i "$payload_file")
    
    echo -e "${BLUE}⏳ API 호출 중...${NC}"
    local start_time=$(date +%s)
    
    if aws bedrock-runtime invoke-model \
        --model-id "$model_id" \
        --body "$encoded_payload" \
        --content-type "application/json" \
        --region "$region" \
        "$response_file" 2>"$error_file"; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        echo -e "${GREEN}✅ 성공! (소요시간: ${duration}초)${NC}"
        
        # 응답 파싱 및 출력
        local content=$(jq -r '.content[0].text' "$response_file" 2>/dev/null || echo "응답 파싱 실패")
        local input_tokens=$(jq -r '.usage.input_tokens // "N/A"' "$response_file" 2>/dev/null)
        local output_tokens=$(jq -r '.usage.output_tokens // "N/A"' "$response_file" 2>/dev/null)
        local total_tokens="N/A"
        if [[ "$input_tokens" != "N/A" && "$output_tokens" != "N/A" ]]; then
            total_tokens=$((input_tokens + output_tokens))
        fi
        
        # 비용 계산
        local cost=$(calculate_cost "$model_name" "$input_tokens" "$output_tokens")
        
        echo -e "${YELLOW}📊 토큰 사용량:${NC}"
        echo -e "   입력 토큰: ${input_tokens}"
        echo -e "   출력 토큰: ${output_tokens}"
        echo -e "   총 토큰: ${total_tokens}"
        
        if [[ "$cost" != "N/A" ]]; then
            echo -e "${YELLOW}💰 예상 비용: \$${cost} USD${NC}"
            
            # $1 목표 달성 여부 확인
            local cost_check=$(awk "BEGIN {print ($cost >= 1.0) ? 1 : 0}")
            if [[ "$cost_check" == "1" ]]; then
                echo -e "${GREEN}🎯 \$1+ 비용 목표 달성!${NC}"
            else
                echo -e "${YELLOW}⚠️  \$1 미만 비용 (목표 미달성)${NC}"
            fi
        else
            echo -e "${RED}💰 비용 계산 실패${NC}"
        fi
        
        echo -e "${GREEN}💬 응답 미리보기:${NC}"
        echo "$content" | head -c 1000
        if [ ${#content} -gt 1000 ]; then
            echo "..."
            echo -e "${BLUE}(응답이 길어서 처음 1000자만 표시)${NC}"
        fi
        echo ""
        
    else
        echo -e "${RED}❌ 실패: 모델 호출 중 오류 발생${NC}"
        if [ -f "$error_file" ] && [ -s "$error_file" ]; then
            echo -e "${RED}오류 내용:${NC}"
            cat "$error_file"
        fi
    fi
    
    # 임시 파일 정리
    rm -f "$payload_file" "$response_file" "$error_file"
    echo -e "${NC}----------------------------------------${NC}"
}

# Check prerequisites
check_requirements() {
    # AWS CLI 설치 확인
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI가 설치되지 않았습니다.${NC}"
        exit 1
    fi
    
    # jq 설치 확인
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq가 설치되지 않았습니다.${NC}"
        echo "macOS: brew install jq"
        exit 1
    fi
    
    # AWS 자격 증명 확인
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS 자격 증명이 설정되지 않았습니다.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 모든 사전 요구사항이 충족되었습니다.${NC}"
}

# Main function
main() {
    local prompt="$DEFAULT_PROMPT"
    local region=""
    local model=""
    local high_cost=false
    local repeat_until_dollar=false
    local all_models=false
    local all_regions=false
    
    # 명령행 인수 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--prompt)
                prompt="$2"
                shift 2
                ;;
            -m|--model)
                model="$2"
                shift 2
                ;;
            -r|--region)
                region="$2"
                shift 2
                ;;
            --all-models)
                all_models=true
                shift
                ;;
            --all-regions)
                all_regions=true
                shift
                ;;
            --high-cost)
                high_cost=true
                shift
                ;;
            --repeat-until-dollar)
                repeat_until_dollar=true
                high_cost=true  # 반복 모드에서는 자동으로 고비용 모드 활성화
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}알 수 없는 옵션: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done
    
    # 사전 요구사항 확인
    check_requirements
    
    # 기본값 설정
    if [[ "$all_models" == false && -z "$model" ]]; then
        model="claude-3-haiku"
    fi
    if [[ "$all_regions" == false && -z "$region" ]]; then
        region="ap-northeast-2"
    fi
    
    # 테스트할 모델 목록 결정
    local models_to_test=()
    if [[ "$all_models" == true ]]; then
        models_to_test=("${CLAUDE_MODEL_NAMES[@]}")
    else
        models_to_test=("$model")
    fi
    
    # 테스트할 리전 목록 결정
    local regions_to_test=()
    if [[ "$all_regions" == true ]]; then
        regions_to_test=("${REGIONS[@]}")
    else
        regions_to_test=("$region")
    fi
    
    echo -e "${BLUE}🚀 AWS Bedrock Claude 모델 테스트 시작${NC}"
    echo -e "${YELLOW}📋 테스트 설정:${NC}"
    echo -e "   모델: ${models_to_test[*]}"
    echo -e "   리전: ${regions_to_test[*]}"
    echo -e "   고비용 모드: $high_cost"
    echo -e "   반복 모드: $repeat_until_dollar"
    echo "================================================================================"
    
    # 각 모델과 리전 조합에 대해 테스트 실행
    for test_model in "${models_to_test[@]}"; do
        for test_region in "${regions_to_test[@]}"; do
            echo -e "${BLUE}🔄 테스트 중: $test_model @ $test_region${NC}"
            
            # 모델 ID 가져오기
            local model_id=$(get_model_id "$test_model" "$test_region")
            if [[ -z "$model_id" ]]; then
                echo -e "${RED}❌ 지원하지 않는 모델: $test_model in $test_region${NC}"
                continue
            fi
            
            # 테스트 실행
            if [[ "$repeat_until_dollar" == true ]]; then
                invoke_claude_model_until_dollar "$test_model" "$model_id" "$prompt" "$test_region" "$high_cost"
                # $1 달성 시 전체 테스트 종료
                if [[ $? -eq 0 ]]; then
                    echo -e "${GREEN}🎉 $1 목표 달성으로 전체 테스트 완료!${NC}"
                    return 0
                fi
            else
                invoke_claude_model "$test_model" "$model_id" "$prompt" "$test_region" "$high_cost"
            fi
            
            echo ""
        done
    done
    
    echo -e "${GREEN}✅ 모든 테스트 완료!${NC}"
}

main "$@"