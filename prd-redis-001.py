import subprocess
import json
from datetime import datetime, timedelta
import pytz

# 시간대 설정
timezone = pytz.timezone("Asia/Seoul")

# maintenance_start_time 변수에 24시간 전 시간을 저장
maintenance_start_time = datetime.now(tz=timezone) - timedelta(hours=24)

# end_time 변수에 현재 시간을 저장
end_time = datetime.now(tz=timezone)

# AWS CLI 명령어 실행
cmd = "aws cloudwatch get-metric-statistics --profile IDL --namespace AWS/ElastiCache \
--metric-name CPUUtilization \
--start-time {maintenance_start_time.strftime('%Y-%m-%dT%H:%M:%SZ')} \
--end-time {end_time.strftime('%Y-%m-%dT%H:%M:%SZ')} \
--period 300 \
--statistics Maximum \
--dimensions Name=CacheClusterId,Value=id-dev-an2-ec-a-redis Name=CacheNodeId,Value=0001"

result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf-8')

if result.returncode != 0:
    print(f"Error running command {cmd}")
else:
    data = json.loads(result.stdout)

# 데이터 처리
count = 0
datapoints = []

for datapoint in data['Datapoints']:
    # Timestamp 값을 datetime 객체로 변환
    datapoint['Timestamp'] = datetime.strptime(datapoint['Timestamp'], '%Y-%m-%dT%H:%M:%S%z')
    if datapoint['Maximum'] >= 1:
        count += 1
        # KST 시간으로 변경
        kst_time = datapoint['Timestamp'].astimezone(timezone)
        datapoint['KST_Time'] = kst_time.strftime('%Y-%m-%d %H:%M:%S')

        datapoints.append(datapoint)

# KST 시간을 기준으로 정렬
datapoints = sorted(datapoints, key=lambda x: x['KST_Time'])

# 정렬된 데이터를 파일에 쓰기
with open('redis001_over70.json', 'w') as output_f:
    for idx, datapoint in enumerate(datapoints, start=1):
        output_f.write(f"{idx}. {datapoint}\n")