# 🚂 Railway 배포 가이드

[English](./DEPLOYMENT.md) | **한국어**

이 가이드는 Railway를 사용하여 AI 결혼 청첩장을 배포하는 방법을 단계별로 설명합니다.

## 📋 목차

- [Railway란?](#railway란)
- [배포 전 준비사항](#배포-전-준비사항)
- [CLI로 배포하기](#cli로-배포하기)
- [GitHub 연동 배포](#github-연동-배포)
- [PostgreSQL 설정](#postgresql-설정)
- [환경변수 설정](#환경변수-설정)
- [커스텀 도메인 연결](#커스텀-도메인-연결)
- [문제 해결](#문제-해결)

## Railway란?

[Railway](https://railway.app/)는 클라우드 애플리케이션 배포 플랫폼입니다.

### 왜 Railway인가?

✅ **무료 티어**
- 월 $5 크레딧 제공
- 소규모 프로젝트에 충분

✅ **간편한 배포**
- Git push만으로 자동 배포
- 복잡한 설정 불필요

✅ **PostgreSQL 통합**
- 원클릭 데이터베이스 생성
- 자동 연결 설정

✅ **자동 SSL**
- HTTPS 자동 적용
- 인증서 관리 불필요

✅ **Zero Config**
- Dockerfile 자동 생성
- 환경 자동 감지

### 비용 안내

**Hobby Plan (무료)**
- 월 $5 크레딧
- 512 MB RAM
- 1 GB 디스크
- 소규모 결혼식(~200명)에 적합

**예상 사용량**
```
웹 서비스: ~$3/월
PostgreSQL: ~$1/월
총 예상: ~$4/월 (무료 범위 내)
```

**결혼식 후에는?**
- 프로젝트 pause 가능
- 데이터는 보존됨
- 필요시 언제든 재개

## 배포 전 준비사항

### 1. Railway 계정 생성

1. [Railway 웹사이트](https://railway.app/) 방문
2. "Sign Up" 클릭
3. GitHub 계정으로 로그인

### 2. 필수 파일 확인

프로젝트에 다음 파일들이 있는지 확인:

```
wedding-invitation/
├── main.py
├── requirements.txt
├── .env.example
├── config/
│   ├── config.json
│   └── couple_knowledge.json
└── (기타 파일들)
```

### 3. 환경변수 준비

배포에 필요한 환경변수 값들을 미리 준비:

- `OPENAI_API_KEY`: OpenAI API 키
- `ADMIN_USERNAME`: 관리자 아이디
- `ADMIN_PASSWORD_HASH`: 관리자 비밀번호 해시
- `SECRET_KEY`: 세션 암호화 키
- `KAKAO_APP_KEY`: (선택) 카카오 앱 키

**관리자 비밀번호 해시 생성:**
```bash
python scripts/generate_password_hash.py
```

**SECRET_KEY 생성:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## CLI로 배포하기

Railway CLI를 사용한 배포 방법입니다.

### 1. Railway CLI 설치

```bash
# npm 사용
npm i -g @railway/cli

# 또는 Homebrew (macOS)
brew install railway
```

### 2. Railway 로그인

```bash
railway login
```

브라우저가 열리면 권한을 승인합니다.

### 3. 프로젝트 초기화

```bash
# 프로젝트 디렉토리로 이동
cd wedding-invitation

# Railway 프로젝트 생성
railway init
```

프롬프트가 나타나면:
- "Create a new project" 선택
- 프로젝트 이름 입력 (예: my-wedding-invitation)

### 4. PostgreSQL 추가

```bash
# PostgreSQL 플러그인 추가
railway add -d postgres
```

### 5. 환경변수 설정

```bash
# 환경변수 설정 (한 줄씩)
railway variables set OPENAI_API_KEY="your_api_key"
railway variables set ADMIN_USERNAME="admin"
railway variables set ADMIN_PASSWORD_HASH="your_hash"
railway variables set SECRET_KEY="your_secret_key"
railway variables set KAKAO_APP_KEY="your_kakao_key"

# (선택) LangSmith
railway variables set LANGCHAIN_API_KEY="your_langsmith_key"
railway variables set LANGCHAIN_TRACING_V2="true"
railway variables set LANGSMITH_PROJECT="wedding-chatbot"
```

### 6. 배포

```bash
# 첫 배포
railway up

# 배포 후 URL 확인
railway open
```

배포가 완료되면 자동으로 브라우저가 열립니다!

### 7. 로그 확인

```bash
# 실시간 로그 보기
railway logs

# 에러만 보기
railway logs -f
```

## GitHub 연동 배포

Git push만으로 자동 배포되도록 설정하는 방법입니다.

### 1. GitHub 저장소 생성

```bash
# Git 초기화 (아직 안 했다면)
git init

# GitHub에 저장소 생성 후
git remote add origin https://github.com/yourusername/wedding-invitation.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2. Railway 프로젝트 생성

1. [Railway 대시보드](https://railway.app/dashboard) 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. 저장소 선택

### 3. PostgreSQL 추가

1. 프로젝트 페이지에서 "New" 클릭
2. "Database" → "Add PostgreSQL" 선택
3. 자동으로 `DATABASE_URL` 환경변수가 설정됩니다

### 4. 환경변수 설정

1. 프로젝트 페이지에서 서비스 클릭
2. "Variables" 탭 선택
3. "New Variable" 클릭하여 추가:

```
OPENAI_API_KEY=your_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hash
SECRET_KEY=your_secret_key
KAKAO_APP_KEY=your_kakao_key
```

### 5. 배포 설정

1. "Settings" 탭 선택
2. 다음 설정 확인:

```
Build Command: (비워두기 - 자동 감지)
Start Command: python main.py
```

### 6. 배포 트리거

```bash
# main 브랜치에 push하면 자동 배포
git add .
git commit -m "Update wedding info"
git push origin main
```

Railway가 자동으로:
1. 코드 pull
2. 의존성 설치
3. 애플리케이션 빌드
4. 배포

## PostgreSQL 설정

Railway PostgreSQL의 자동 설정과 수동 관리 방법입니다.

### 자동 설정 (권장)

Railway가 자동으로:
- PostgreSQL 인스턴스 생성
- `DATABASE_URL` 환경변수 설정
- 애플리케이션과 자동 연결

추가 작업 불필요!

### 수동 연결 (고급)

특정 PostgreSQL 서버를 사용하려면:

```bash
# 환경변수로 수동 설정
railway variables set DATABASE_URL="postgresql://user:password@host:port/database"
```

### 데이터베이스 접근

**Railway CLI로 접근:**
```bash
# PostgreSQL 콘솔 열기
railway connect postgres
```

**외부 클라이언트로 접근:**
1. Railway 대시보드에서 PostgreSQL 서비스 선택
2. "Connect" 탭에서 연결 정보 확인
3. pgAdmin, DBeaver 등으로 연결

### 백업

**자동 백업:**
Railway는 자동으로 백업하지 않습니다.

**수동 백업 (중요!):**
```bash
# 로컬로 백업
railway run pg_dump $DATABASE_URL > backup.sql

# 복구
railway run psql $DATABASE_URL < backup.sql
```

**정기 백업 설정:**
결혼식 전후로 정기적으로 백업하는 것을 권장합니다.

## 환경변수 설정

Railway에서 환경변수를 효율적으로 관리하는 방법입니다.

### 대시보드에서 설정

1. 프로젝트 → 서비스 선택
2. "Variables" 탭
3. "New Variable" 클릭

### CLI로 설정

```bash
# 단일 변수 설정
railway variables set KEY="value"

# 여러 변수 한번에 설정
railway variables set \
  KEY1="value1" \
  KEY2="value2" \
  KEY3="value3"

# 변수 확인
railway variables

# 변수 삭제
railway variables delete KEY
```

### .env 파일에서 가져오기

```bash
# .env 파일의 모든 변수를 Railway에 업로드
while IFS= read -r line; do
  if [[ ! "$line" =~ ^#.*$ ]] && [[ -n "$line" ]]; then
    railway variables set "${line%%=*}=${line#*=}"
  fi
done < .env
```

### 환경별 변수 관리

**개발 환경:**
```bash
# .env.development
DEBUG=true
LOG_LEVEL=debug
```

**프로덕션 환경 (Railway):**
```bash
# Railway 변수로 설정
DEBUG=false
LOG_LEVEL=info
```

### 민감 정보 보호

⚠️ **절대 Git에 커밋하지 마세요:**
- API 키
- 비밀번호
- 데이터베이스 URL
- SECRET_KEY

✅ **올바른 방법:**
1. `.env.example` 파일만 커밋
2. 실제 값은 Railway 환경변수로 설정
3. `.gitignore`에 `.env` 추가

## 커스텀 도메인 연결

Railway 기본 도메인(예: `your-app.railway.app`) 대신 자신의 도메인을 사용하는 방법입니다.

### 1. 도메인 구매

도메인 등록 대행사에서 도메인 구매:
- [가비아](https://www.gabia.com/)
- [Namecheap](https://www.namecheap.com/)
- [GoDaddy](https://www.godaddy.com/)

추천 도메인 예시:
- `soohwan-soyoung-wedding.com`
- `김수환-조소영.com`
- `wedding-2026.com`

### 2. Railway에 도메인 추가

1. Railway 프로젝트의 서비스 선택
2. "Settings" 탭
3. "Domains" 섹션
4. "Custom Domain" 입력 (예: `www.your-domain.com`)

### 3. DNS 설정

도메인 등록 대행사의 DNS 관리 페이지에서:

**CNAME 레코드 추가:**
```
Type: CNAME
Name: www (또는 @)
Value: your-app.railway.app
TTL: Auto (또는 3600)
```

**예시 (가비아):**
1. "My가비아" → "서비스 관리"
2. 도메인 선택 → "DNS 정보" → "설정"
3. 레코드 추가:
   - 타입: CNAME
   - 호스트: www
   - 값/위치: your-app.railway.app

### 4. SSL 인증서

Railway가 자동으로 Let's Encrypt SSL 인증서를 발급합니다.
- HTTPS 자동 적용
- 인증서 자동 갱신
- 추가 설정 불필요

### 5. 리디렉션 설정 (선택)

`example.com` → `www.example.com` 리디렉션:

도메인 DNS에 추가:
```
Type: A
Name: @
Value: 76.76.21.21 (Railway의 IP)
```

또는 URL Redirect 레코드 사용 (등록 대행사마다 다름)

### 검증

1. DNS 전파 확인 (최대 48시간 소요):
```bash
nslookup www.your-domain.com
```

2. 브라우저에서 접속:
```
https://www.your-domain.com
```

3. SSL 인증서 확인:
주소창의 자물쇠 아이콘 클릭

## 문제 해결

### 배포가 실패해요

**증상:** "Build failed" 또는 "Deployment failed" 에러

**해결 1: 로그 확인**
```bash
railway logs
```

**해결 2: 의존성 문제**
```bash
# requirements.txt 확인
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

**해결 3: 파이썬 버전 지정**
```bash
# runtime.txt 파일 생성
echo "python-3.11" > runtime.txt
```

### 데이터베이스 연결 오류

**증상:** "Database connection failed"

**해결 1: DATABASE_URL 확인**
```bash
railway variables | grep DATABASE_URL
```

**해결 2: PostgreSQL 재시작**
1. Railway 대시보드
2. PostgreSQL 서비스 선택
3. "Settings" → "Restart"

**해결 3: 연결 문자열 확인**
```python
# main.py에서 로그 확인
import os
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
```

### 애플리케이션이 시작되지 않아요

**증상:** "Application failed to start"

**해결 1: 포트 설정 확인**
```python
# main.py
port = int(os.getenv("PORT", 8000))
uvicorn.run("main:app", host="0.0.0.0", port=port)
```

**해결 2: 환경변수 확인**
```bash
railway variables
```

필수 환경변수가 모두 설정되어 있는지 확인

**해결 3: 헬스체크**
Railway가 애플리케이션이 준비되었는지 확인:
```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### 챗봇이 작동하지 않아요

**증상:** 챗봇 응답이 없거나 에러 발생

**해결 1: OpenAI API 키 확인**
```bash
railway variables | grep OPENAI_API_KEY
```

**해결 2: 지식베이스 파일 확인**
```bash
# config 파일들이 배포되었는지 확인
railway run ls -la config/
```

**해결 3: 로그 확인**
```bash
railway logs | grep chatbot
railway logs | grep ERROR
```

### 사이트가 느려요

**증상:** 페이지 로딩이 느림

**해결 1: 무료 플랜 확인**
Railway 무료 플랜은 512MB RAM 제한이 있습니다.

**해결 2: 이미지 최적화**
```bash
# WebP 변환 스크립트 실행
python scripts/resize_image.py
```

**해결 3: 업그레이드 고려**
트래픽이 많다면 Hobby Plan ($5/월) 고려

### 도메인이 연결되지 않아요

**증상:** 커스텀 도메인으로 접속 안 됨

**해결 1: DNS 전파 확인**
```bash
nslookup www.your-domain.com
```

**해결 2: 시간 대기**
DNS 전파는 최대 48시간 소요될 수 있습니다.

**해결 3: DNS 레코드 확인**
- 정확한 CNAME 값 입력 확인
- Railway 대시보드에서 도메인 상태 확인

### 비용이 예상보다 많이 나와요

**증상:** 월 $5 크레딧 초과

**해결 1: 사용량 확인**
1. Railway 대시보드
2. "Usage" 탭
3. 서비스별 사용량 확인

**해결 2: 불필요한 서비스 중지**
```bash
# 사용하지 않는 서비스 삭제
railway service delete SERVICE_NAME
```

**해결 3: 모델 변경**
```bash
# 더 저렴한 GPT 모델 사용
railway variables set CHAT_MODEL="gpt-3.5-turbo"
```

## 배포 체크리스트

배포 전 확인사항:

### 배포 전
- [ ] OpenAI API 키 준비
- [ ] 관리자 비밀번호 해시 생성
- [ ] SECRET_KEY 생성
- [ ] config.json 작성 완료
- [ ] couple_knowledge.json 작성 완료
- [ ] 이미지 파일 최적화 (WebP)
- [ ] requirements.txt 업데이트

### Railway 설정
- [ ] Railway 계정 생성
- [ ] PostgreSQL 추가
- [ ] 환경변수 모두 설정
- [ ] GitHub 저장소 연결 (자동 배포 사용 시)

### 배포 후
- [ ] 사이트 접속 확인
- [ ] 챗봇 테스트
- [ ] 방명록 테스트
- [ ] RSVP 테스트
- [ ] 관리자 페이지 로그인 테스트
- [ ] 모바일 반응형 확인
- [ ] 카카오톡 공유 테스트 (선택)
- [ ] 데이터베이스 백업

### 결혼식 당일
- [ ] 서버 상태 모니터링
- [ ] 로그 확인
- [ ] 데이터베이스 백업

### 결혼식 후
- [ ] 방명록 CSV 다운로드
- [ ] RSVP 데이터 CSV 다운로드
- [ ] 데이터베이스 최종 백업
- [ ] 프로젝트 pause (비용 절감)

## 추가 리소스

### Railway 공식 문서
- [Railway 문서](https://docs.railway.app/)
- [CLI 문서](https://docs.railway.app/develop/cli)
- [환경변수 가이드](https://docs.railway.app/develop/variables)

### 커뮤니티
- [Railway Discord](https://discord.gg/railway)
- [Railway 블로그](https://blog.railway.app/)

### 관련 가이드
- [설치 가이드](./INSTALLATION.ko.md)
- [설정 가이드](./CONFIGURATION.ko.md)
- [AI 챗봇 가이드](./CHATBOT.ko.md)

## 도움이 필요하신가요?

- 📧 [이메일 문의](mailto:your.email@example.com)
- 💬 [디스코드 커뮤니티](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)

---

**축하합니다! 🎉** 

성공적으로 배포되었다면, 이제 하객들과 청첩장을 공유하고 AI 챗봇과 대화를 나눌 수 있습니다!