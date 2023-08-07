## 00. 사전준비
### 00-01. flight_delays_iceberg Folder 생성
- 대상폴더 : s3://<자동생성버킷명>/iceberg/
- 생성폴더명 : flight_delays_iceberg
- 생성후모습 : s3://<자동생성버킷명>/iceberg/flight_delays_iceberg/
### 00-02. Athena 기본 설정
- Athena 서비스 이동 : https://us-east-1.console.aws.amazon.com/athena/home?region=us-east-1#/query-editor
- Athena QueryLog 설정 : s3://<자동생성버킷명>/athenaqueryresults/ 

## 01. 소스 데이터 인 Hive Parquet 테이블 셋팅
### 01-01. Hive EXTERNAL 테이블 생성
```sql
CREATE EXTERNAL TABLE iceberg.flight_delays_pq (
    yr INT,
    quarter INT,
    month INT,
    dayofmonth INT,
    dayofweek INT,
    flightdate STRING,
    uniquecarrier STRING,
    airlineid INT,
    carrier STRING,
    tailnum STRING,
    flightnum STRING,
    originairportid INT,
    originairportseqid INT,
    origincitymarketid INT,
    origin STRING,
    origincityname STRING,
    originstate STRING,
    originstatefips STRING,
    originstatename STRING,
    originwac INT,
    destairportid INT,
    destairportseqid INT,
    destcitymarketid INT,
    dest STRING,
    destcityname STRING,
    deststate STRING,
    deststatefips STRING,
    deststatename STRING,
    destwac INT,
    crsdeptime STRING,
    deptime STRING,
    depdelay INT,
    depdelayminutes INT,
    depdel15 INT,
    departuredelaygroups INT,
    deptimeblk STRING,
    taxiout INT,
    wheelsoff STRING,
    wheelson STRING,
    taxiin INT,
    crsarrtime INT,
    arrtime STRING,
    arrdelay INT,
    arrdelayminutes INT,
    arrdel15 INT,
    arrivaldelaygroups INT,
    arrtimeblk STRING,
    cancelled INT,
    cancellationcode STRING,
    diverted INT,
    crselapsedtime INT,
    actualelapsedtime INT,
    airtime INT,
    flights INT,
    distance INT,
    distancegroup INT,
    carrierdelay INT,
    weatherdelay INT,
    nasdelay INT,
    securitydelay INT,
    lateaircraftdelay INT,
    firstdeptime STRING,
    totaladdgtime INT,
    longestaddgtime INT,
    divairportlandings INT,
    divreacheddest INT,
    divactualelapsedtime INT,
    divarrdelay INT,
    divdistance INT,
    div1airport STRING,
    div1airportid INT,
    div1airportseqid INT,
    div1wheelson STRING,
    div1totalgtime INT,
    div1longestgtime INT,
    div1wheelsoff STRING,
    div1tailnum STRING,
    div2airport STRING,
    div2airportid INT,
    div2airportseqid INT,
    div2wheelson STRING,
    div2totalgtime INT,
    div2longestgtime INT,
    div2wheelsoff STRING,
    div2tailnum STRING,
    div3airport STRING,
    div3airportid INT,
    div3airportseqid INT,
    div3wheelson STRING,
    div3totalgtime INT,
    div3longestgtime INT,
    div3wheelsoff STRING,
    div3tailnum STRING,
    div4airport STRING,
    div4airportid INT,
    div4airportseqid INT,
    div4wheelson STRING,
    div4totalgtime INT,
    div4longestgtime INT,
    div4wheelsoff STRING,
    div4tailnum STRING,
    div5airport STRING,
    div5airportid INT,
    div5airportseqid INT,
    div5wheelson STRING,
    div5totalgtime INT,
    div5longestgtime INT,
    div5wheelsoff STRING,
    div5tailnum STRING
)
PARTITIONED BY (year STRING)
STORED AS PARQUET
LOCATION 's3://athena-examples-us-east-1/flight/parquet/'
tblproperties ("parquet.compression"="SNAPPY");
```

### 01-02. 빈 데이터확인
```sql
select * from iceberg.flight_delays_pq limit 5;
```

### 01-03. Partition Upload
```sql
MSCK REPAIR TABLE iceberg.flight_delays_pq;
```

### 01-04. 업로드 된 최종 데이터확인
```sql
select * from iceberg.flight_delays_pq limit 5;

SELECT origin, dest, count(*) as delays
FROM iceberg.flight_delays_pq
WHERE depdelayminutes > 60
GROUP BY origin, dest
ORDER BY 3 DESC
LIMIT 10;
```


## 2. iceberg table 구성
### 2.1. Create Iceberg Table 
#### !! 주의 : 버킷명 변경
```sql
CREATE TABLE iceberg.flight_delays_iceberg(
    year STRING,
    month INT,
    flightdate STRING,
    airlineid INT,
    carrier STRING,
    flightnum STRING,
    originairportid INT,
    origin STRING,
    destairportid INT,
    dest STRING
)
PARTITIONED BY (year)
LOCATION 's3://<자동생성버킷명>/iceberg/flight_delays_iceberg/'
TBLPROPERTIES (
'table_type'='ICEBERG',
'format'='parquet'
)
```
### 2.2. Metadata.json 파일 생성 확인 
- s3에 메타데이터 확인 : s3://<자동생성버킷명>/iceberg/flight_delays_iceberg/metadata/~~.metadata.json

### 2.3. 빈 iceberg table 확인
```sql
select * from iceberg.flight_delays_iceberg limit 10;

select count(1) from iceberg.flight_delays_iceberg;
```

## 3. 데이터 입력
### 3.1. iceberg table 데이터 입력 ( 소스는 Hive 테이블로부터 읽어 옴 )
```sql
insert into iceberg.flight_delays_iceberg
select
    year,
    month,
    flightdate,
    airlineid,
    carrier,
    flightnum,
    originairportid,
    origin,
    destairportid,
    dest
from iceberg.flight_delays_pq
where year in ('2011','2012','2013','2014','2015','2016');
-- 약 10초 ~ 30초 소요
```

### 3.2. insert 된 데이터 확인
```sql
select * from iceberg.flight_delays_iceberg limit 10;

select count(1) from iceberg.flight_delays_iceberg; -- 31,060,131 건
```

### 3.3. s3에 데이터 확인
- data 폴더가 생김
- metadata 폴더 하위 새로생긴 metadata.json, manifest_list.avro, manifest.avro 파일 확인
- data 폴더 하위 실제 데이터 Parquet 파일 생성

## 4. 스키마 변경 - Evolving Iceberg table schema
### 4.1. comment 컬럼 추가
```sql
ALTER TABLE iceberg.flight_delays_iceberg ADD COLUMNS (comment string)
```
- metadata폴더에 Metadata.json 추가된 내용, 특히, Schema 버전 관리 확인

### 4.2. comment 값 Update
```sql
UPDATE iceberg.flight_delays_iceberg
SET comment = 'Comment for 2016'
Where year = '2016';
```
- metadata폴더에 Metadata.json, manifest list , manifest 파일 확인

### 4.3. Update 후 commnet 값 확인
```sql
select year,comment from iceberg.flight_delays_iceberg
where year = '2016'
limit 5
```

## 5. Time Travel
### 5.1. 테이블의 Snapshot 이력 확인
```sql
SELECT * FROM "iceberg"."flight_delays_iceberg$history"
```

### 5.2. 이전 Snapshot 이력 확인
```sql
select * from iceberg.flight_delays_iceberg FOR VERSION AS OF <pre_snapshop_id>
where year = '2016'
limit 5
```

### 5.3. 이전 Snapshot 이력 확인 (오류발생)
```sql
select year, comment from iceberg.flight_delays_iceberg FOR VERSION AS OF <pre_snapshop_id>
where year = '2016'
limit 5
```
- 이전 Snapshot에서는 comment 컬럼이 없어서 오류발생 

## 6. 데이터 삭제
### 6.1. 2011년 데이터 Delete 수행
```sql
delete from iceberg.flight_delays_iceberg
where year = '2011'
```

### 6.2. 삭제된 데이터 확인
```sql
select year,comment from iceberg.flight_delays_iceberg
where year = '2011'
```

## 7. Snapshop으로 부터 데이터 복구 
### 7.1. 데이터 복구를 위해 테이블 히스토리 확인
```sql
SELECT * FROM "iceberg"."flight_delays_iceberg$history"
```

### 7.2. 데이터 복구 전 이전 히스토리 데이터 확인
```sql
select * from iceberg.flight_delays_iceberg FOR VERSION AS OF <<Enter Snapshot ID>>
where year = '2011' limit 10
```

### 7.3. 데이터 복구
```sql
insert into iceberg.flight_delays_iceberg
select * from iceberg.flight_delays_iceberg FOR VERSION AS OF <<Enter Snapshot ID>>
where year = '2011' limit 10
```

### 7.4. 복구된 2011년 데이터 확인
```sql
select count(1) cnt from iceberg.flight_delays_iceberg
where year = '2011'
```