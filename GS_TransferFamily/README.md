[사전정의사항]
1. EFS는 이미 만들어져있다고 가정 * EFS 생성시 Network 셋팅에  Security Group 셋팅 유의
2. Posix 설정을 위한 Bastion Host는 미리 만들어져 있다고 가정 ( 여기선 Cloud 9 사용)

## 01. SFTP + Identity provider type (Service Managed)

### PKI 방식 로그인을 위하여 PKI 키 생성
    
    ssh-keygen -t rsa -b 4096 -f transfer-key

* 참조 : https://docs.aws.amazon.com/transfer/latest/userguide/key-management.html#macOS-linux-unix-ssh

### Transfer Family 환경 생성

#### Choose_protocols
![Choose_protocols](01.SFTP_ServiceManaged_Public/01-01.Choose_protocols.png)

#### Choose_an_identity_provider
![Choose_an_identity_provider](01.SFTP_ServiceManaged_Public/01-02.Choose_an_identity_provider.png)

#### Choose_an_endpoint
![Choose_an_endpoint](01.SFTP_ServiceManaged_Public/01-03.Choose_an_endpoint.png)

#### Choose_a_domain
![Choose_a_domain](01.SFTP_ServiceManaged_Public/01-04.Choose_a_domain.png)

#### Configure_additional_details

- 모든 항목 Default로 선택 후 Next

![Choose_a_domain](01.SFTP_ServiceManaged_Public/01-05.Configure_additional_details.png)

### Cloud9(or Bastion Host)에서 mount 하여, 필요한 폴더 생성 및 파일 권한 작업을 한다.

#### Install dependencies
    sudo yum install jq amazon-efs-utils -y

#### 마운트 생성
    sudo mkdir [마운트_폴더]
    ex) sudo mkdir /mnt/efs

    sudo mount -t efs -o tls,mounttargetip=[EFS_MOUNT_TARGET_IP] [EFS_FILESYSTEM]:/ [마운트폴더]
    ex) sudo mount -t efs -o tls,mounttargetip=10.0.2.27 fs-09f9ab6c8a690f21c:/ /mnt/efs

#### 폴더 생성 및 권한 셋팅

    sudo mkdir -p [마운트폴더]/[업체코드]
    sudo chmod 751 [마운트폴더]/[업체코드]*
    sudo chgrp -R [GID] [마운트폴더]/[업체코드]
    sudo chown [UID] [마운트폴더]/[업체코드]

    ex)
    sudo mkdir -p /mnt/efs/vendorA
    sudo chmod 751 /mnt/efs/vendorA*
    sudo chgrp -R 3000 /mnt/efs/vendorA
    sudo chown 3001 /mnt/efs/vendorA

- UID/GID를 업체마다 고유하게 생성하여 폴더 권한관리

### Transfer Family User 생성

#### IAM Role 생성
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "elasticfilesystem:ClientMount",
                    "elasticfilesystem:ClientWrite",
                    "elasticfilesystem:DescribeFileSystems"
                ],
                "Resource": [
                    "[EFS_ARN]"
                ]
            }
        ]
    }

    ex)
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "elasticfilesystem:ClientMount",
                    "elasticfilesystem:ClientWrite",
                    "elasticfilesystem:DescribeFileSystems"
                ],
                "Resource": [
                    "arn:aws:elasticfilesystem:us-east-1:028697689548:file-system/fs-09f9ab6c8a690f21c"
                ]
            }
        ]
    }


#### 업체 User 생성

![Add_user](01.SFTP_ServiceManaged_Public/01-06.Add_user.png)
![Add_user_detail](01.SFTP_ServiceManaged_Public/01-07.Add_user_detail.png)

- User ID : EFS에 셋팅한 업체 POSIX UID
- Group ID : EFS에 셋팅한 업체 POSIX ㅎID
- Role : 위에서 생성한 IAM Role
- Home Directory : EFS 선택 & 업체가 접근가능한 이전에 생성한 폴더명 기재
- Restriced : 체크 - 체크하면 다른 폴더 접근이 안됨. 
  ex) sftp로 접근하면 vendorA 폴더가 root로 보임. 다른 폴더로 갈 수 없음
- SSH public key : transfer-key.pub 파일 열어 내용 복사해서 입력

#### SFTP 테스트 ( 맥환경 )

    sftp -i [개인키파일] [업체ID]@[Transfer_Family_Endpoint]

    ex)
    sftp -i transfer-key vendorA@s-63b351044f5a47119.server.transfer.us-east-1.amazonaws.com

![Result](01.SFTP_ServiceManaged_Public/01-08.Result.png)

- put 명령어 수행 하여 파일 업로드 성공한 화면 







