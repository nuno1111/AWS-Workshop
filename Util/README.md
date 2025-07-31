## 1. 사용할 리전(ap-northeast-2, us-west-2, us-east-1, .... )에서 Bedrock Claude 모델 Model Access Grant 가 필요합니다.
## 2. 사용량은 하나의 리전만 해도 가능해서 us-east-1에서 수행합니다.
## 3. 아래 명령어를 복사하여 Cloud Shell에서 실행합니다.
```shell
cd ~
git clone https://github.com/nuno1111/AWS-Workshop.git 
cd ./AWS-Workshop/Util
chmod +x ./bedrock_claude_awscli_fixed.sh     
./bedrock_claude_awscli_fixed.sh --all-models -r us-east-1

```
