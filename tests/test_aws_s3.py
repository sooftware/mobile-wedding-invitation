"""
AWS S3 연결 테스트 스크립트

이 스크립트는 AWS S3에 파일을 업로드하고 다운로드하는 테스트를 수행합니다.
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# AWS 설정
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_STORAGE_FOLDER = os.getenv("AWS_STORAGE_FOLDER", "wedding-images")

print("=" * 60)
print("AWS S3 연결 테스트")
print("=" * 60)
print(f"리전: {AWS_REGION}")
print(f"버킷: {AWS_BUCKET_NAME}")
print(f"폴더: {AWS_STORAGE_FOLDER}")
print(f"Access Key: {AWS_ACCESS_KEY[:10]}...")
print("=" * 60)

# S3 클라이언트 생성
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    print("\n✅ S3 클라이언트 생성 성공")
except Exception as e:
    print(f"\n❌ S3 클라이언트 생성 실패: {e}")
    exit(1)

# 1. 버킷 목록 조회
print("\n" + "=" * 60)
print("1. 버킷 목록 조회 테스트")
print("=" * 60)
try:
    response = s3_client.list_buckets()
    print("✅ 버킷 목록 조회 성공:")
    for bucket in response['Buckets']:
        print(f"   - {bucket['Name']}")
except ClientError as e:
    print(f"❌ 버킷 목록 조회 실패: {e}")

# 2. 특정 버킷 접근 테스트
print("\n" + "=" * 60)
print(f"2. '{AWS_BUCKET_NAME}' 버킷 접근 테스트")
print("=" * 60)
try:
    response = s3_client.list_objects_v2(
        Bucket=AWS_BUCKET_NAME,
        MaxKeys=5
    )
    file_count = response.get('KeyCount', 0)
    print(f"✅ 버킷 접근 성공 (파일 {file_count}개)")

    if file_count > 0:
        print("   최근 파일:")
        for obj in response.get('Contents', []):
            print(f"   - {obj['Key']} ({obj['Size']} bytes)")
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"❌ 버킷 접근 실패: {error_code}")
    print(f"   상세: {e}")

# 3. 파일 업로드 테스트
print("\n" + "=" * 60)
print("3. 파일 업로드 테스트")
print("=" * 60)

test_content = "안녕하세요! 이것은 AWS S3 테스트 파일입니다."
test_filename = f"../test.sh"

try:
    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=test_filename,
        Body=test_content.encode('utf-8'),
        ContentType='text/plain'
    )
    print(f"✅ 파일 업로드 성공: {test_filename}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"❌ 파일 업로드 실패: {error_code}")
    print(f"   상세: {e}")

    if error_code == 'AccessDenied':
        print("\n⚠️  권한 문제 발견!")
        print("   해결 방법:")
        print("   1. AWS IAM 콘솔에서 해당 사용자의 권한 확인")
        print("   2. S3 버킷 정책에서 PutObject 권한 추가")
        print("   3. IAM 사용자에게 S3FullAccess 또는 커스텀 정책 부여")

# 4. 파일 다운로드 테스트
print("\n" + "=" * 60)
print("4. 파일 다운로드 테스트")
print("=" * 60)
try:
    response = s3_client.get_object(
        Bucket=AWS_BUCKET_NAME,
        Key=test_filename
    )
    downloaded_content = response['Body'].read().decode('utf-8')
    print(f"✅ 파일 다운로드 성공")
    print(f"   내용: {downloaded_content}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"❌ 파일 다운로드 실패: {error_code}")
    if error_code != 'NoSuchKey':
        print(f"   상세: {e}")

# 5. Presigned URL 생성 테스트
print("\n" + "=" * 60)
print("5. Presigned URL 생성 테스트")
print("=" * 60)
try:
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': AWS_BUCKET_NAME,
            'Key': test_filename
        },
        ExpiresIn=300  # 5분
    )
    print(f"✅ Presigned URL 생성 성공")
    print(f"   URL: {presigned_url[:80]}...")
except ClientError as e:
    print(f"❌ Presigned URL 생성 실패: {e}")

# 6. 파일 삭제 테스트
print("\n" + "=" * 60)
print("6. 파일 삭제 테스트")
print("=" * 60)
try:
    s3_client.delete_object(
        Bucket=AWS_BUCKET_NAME,
        Key=test_filename
    )
    print(f"✅ 파일 삭제 성공: {test_filename}")
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"❌ 파일 삭제 실패: {error_code}")
    print(f"   상세: {e}")

# 최종 결과
print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
print("\n모든 테스트를 통과했다면 권한 설정이 올바릅니다.")
print("업로드 실패 시, 위의 권한 설정 방법을 참고하세요.")
