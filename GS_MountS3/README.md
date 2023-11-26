## EC2 사용하는 A 계정에 IAM Role - Policy 설정 후 Role에 할당
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "s3policy",
			"Effect": "Allow",
			"Action": "s3:*",
			"Resource": "arn:aws:s3:::com.gsretail.mount-s3-bucket"
		}
	]
}

## s3 생성된 B계정에 s3 Policy 설정
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::541948677097:role/Role_EC2_Mount_S3"
            },
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::com.gsretail.mount-s3-bucket/*"
        }
    ]
}

## EC2에 mount-s3 설치
$ wget https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.rpm
$ sudo yum install ./mount-s3.rpm

## EC2에 mount 명령어
$ mkdir mnt_s3
$ mount-s3 com.gsretail.mount-s3-bucket mnt_s3

# Redis 접속
redis-cli -h clustercfg.gsretailmemorydbforredis.a8vfny.memorydb.us-east-1.amazonaws.com --user $REDIS_USER --pass $REDIS_PASS --tls -c

redis-cli -h clustercfg.gsretailmemorydbforredis.a8vfny.memorydb.us-east-1.amazonaws.com --tls -c

aws memorydb describe-clusters  --cluster-name gsretailmemorydbforredis --query Clusters[*].ClusterEndpoint.Address --output=text

