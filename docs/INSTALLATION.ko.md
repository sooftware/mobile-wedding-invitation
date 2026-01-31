# 💻 설치 가이드

[English](./INSTALLATION.md) | **한국어**

이 가이드는 AI 결혼 청첩장을 로컬 환경에 설치하고 실행하는 방법을 상세히 설명합니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [설치 과정](#설치-과정)
- [환경변수 설정](#환경변수-설정)
- [설정 파일 작성](#설정-파일-작성)
- [실행 및 테스트](#실행-및-테스트)
- [문제 해결](#문제-해결)

## 시스템 요구사항

### 필수 요구사항

**운영체제:**
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, etc.)

**소프트웨어:**
- Python 3.8 이상 (권장: 3.11)
- pip (Python 패키지 관리자)
- Git (버전 관리)

**하드웨어:**
- CPU: 듀얼 코어 이상
- RAM: 최소 2GB (권장 4GB)
- 디스크: 500MB 이상 여유 공간

### 선택 요구사항

- PostgreSQL 15+ (프로덕션 환경)
- Node.js 18+ (Railway CLI 사용 시)
- 텍스트 에디터 (VS Code, Sublime Text 등)

## 설치 과정

### 1. Python 설치 확인

**Windows:**
```bash
# PowerShell 또는 CMD에서
python --version
```

Python이 설치되지 않았다면:
1. [Python 공식 사이트](https://www.python.org/downloads/) 방문
2. 최신 버전 다운로드 (3.11 권장)
3. 설치 시 "Add Python to PATH" 체크박스 선택

**macOS:**
```bash
# Homebrew로 설치
brew install python@3.11

# 또는 공식 설치 파일 사용
# python.org에서 다운로드
```

**Linux (Ubuntu/Debian):**
```bash
# 시스템 업데이트
sudo apt update
sudo apt upgrade

# Python 설치
sudo apt install python3.11 python3-pip python3-venv
```

**설치 확인:**
```bash
python --version
# 출력: Python 3.11.x

pip --version
# 출력: pip 23.x.x
```

### 2. Git 설치 확인

```bash
git --version
```

Git이 설치되지 않았다면:

**Windows:**
- [Git for Windows](https://git-scm.com/download/win) 다운로드 및 설치

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

### 3. 프로젝트 클론

```bash
# GitHub 저장소 클론
git clone https://github.com/yourusername/wedding-invitation.git

# 프로젝트 디렉토리로 이동
cd wedding-invitation

# 디렉토리 구조 확인
ls -la
```

예상 출력:
```
.
├── app/
├── config/
├── static/
├── templates/
├── scripts/
├── main.py
├── requirements.txt
└── .env.example
```

### 4. 가상환경 생성

가상환경을 사용하면 프로젝트별로 독립적인 Python 패키지를 관리할 수 있습니다.

**생성:**
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

**활성화:**
```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

활성화 확인:
```bash
# 프롬프트 앞에 (venv)가 표시됨
(venv) user@computer:~/wedding-invitation$
```

### 5. 의존성 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 프로젝트 의존성 설치
pip install -r requirements.txt
```

설치되는 주요 패키지:
- fastapi - 웹 프레임워크
- uvicorn - ASGI 서버
- langchain - LLM 프레임워크
- langgraph - 워크플로우 관리
- openai - OpenAI API 클라이언트
- chromadb - 벡터 데이터베이스
- psycopg2-binary - PostgreSQL 드라이버
- boto3 - AWS SDK (S3 스토리지)
- jinja2 - 템플릿 엔진

설치 확인:
```bash
pip list
```

### 6. 환경변수 파일 생성

```bash
# .env.example을 .env로 복사
cp .env.example .env

# Windows에서는
copy .env.example .env
```

`.env` 파일을 텍스트 에디터로 열어 수정합니다.

## 환경변수 설정

### 필수 환경변수

**`.env` 파일:**
```bash
# ===========================================
# OpenAI API 설정 (AI 챗봇용)
# ===========================================
OPENAI_API_KEY=sk-your-openai-api-key-here

# 모델 선택
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# 생성 파라미터
CHAT_TEMPERATURE=0.7
MAX_TOKENS=300
TOP_K_RESULTS=3

# ===========================================
# 관리자 계정 설정
# ===========================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your-generated-hash-here

# ===========================================
# 세션 보안 키
# ===========================================
SECRET_KEY=your-secret-key-here

# ===========================================
# 데이터베이스 (로컬에서는 선택)
# ===========================================
# DATABASE_URL=postgresql://user:password@localhost:5432/wedding
# 설정하지 않으면 SQLite 사용

# ===========================================
# AWS S3 설정 (사진 업로드용)
# ===========================================
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
AWS_BUCKET_NAME=your-bucket-name
AWS_STORAGE_FOLDER=wedding-images

# ===========================================
# 카카오톡 공유 (선택)
# ===========================================
KAKAO_APP_KEY=your-kakao-app-key

# ===========================================
# LangSmith 추적 (선택)
# ===========================================
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your-langsmith-key
# LANGSMITH_PROJECT=wedding-chatbot
```

### OpenAI API 키 발급

1. [OpenAI 플랫폼](https://platform.openai.com/) 접속
2. 로그인 또는 회원가입
3. "API Keys" 메뉴 클릭
4. "Create new secret key" 클릭
5. 키 이름 입력 (예: wedding-chatbot)
6. 생성된 키 복사 (한 번만 표시됨!)
7. `.env` 파일의 `OPENAI_API_KEY`에 붙여넣기

**보안 주의:**
- ⚠️ API 키를 절대 GitHub에 커밋하지 마세요
- ⚠️ 공개적으로 공유하지 마세요
- ✅ `.env` 파일은 `.gitignore`에 포함되어 있음

### 관리자 비밀번호 설정

**1. 비밀번호 해시 생성:**
```bash
python scripts/generate_password_hash.py
```

**2. 실행 화면:**
```
🔐 관리자 비밀번호 해시 생성 도구
========================================

새 비밀번호를 입력하세요: [입력]
비밀번호를 다시 입력하세요: [입력]

✅ 비밀번호 해시가 생성되었습니다!
========================================

📋 .env 파일에 다음 내용을 추가하세요:

ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

**3. `.env` 파일에 복사:**
```bash
ADMIN_PASSWORD_HASH=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

### SECRET_KEY 생성

세션 암호화를 위한 랜덤 키 생성:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

출력 예시:
```
xK8vN2pQmR5wT1yU3zL7hA9bC4dE6fG8
```

`.env` 파일에 추가:
```bash
SECRET_KEY=xK8vN2pQmR5wT1yU3zL7hA9bC4dE6fG8
```

### AWS S3 설정 (사진 업로드용)

사진 업로드 기능을 사용하려면 AWS S3 버킷이 필요합니다:

**1. AWS 계정 생성 및 S3 버킷 생성:**
1. [AWS Console](https://aws.amazon.com/) 접속
2. S3 서비스로 이동
3. "버킷 만들기" 클릭
4. 버킷 이름 입력 (예: my-wedding-photos)
5. 리전 선택 (ap-northeast-2 권장 - 서울)
6. 버킷 생성 완료

**2. IAM 사용자 생성 및 액세스 키 발급:**
1. IAM 서비스로 이동
2. "사용자" → "사용자 추가"
3. 사용자 이름 입력 (예: wedding-app-user)
4. "프로그래밍 방식 액세스" 선택
5. 권한: "AmazonS3FullAccess" 정책 연결
6. 액세스 키 ID와 비밀 액세스 키 저장

**3. `.env` 파일에 추가:**
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalr...
AWS_REGION=ap-northeast-2
AWS_BUCKET_NAME=my-wedding-photos
AWS_STORAGE_FOLDER=wedding-images
```

⚠️ **보안 주의사항:**
- AWS 액세스 키를 절대 GitHub에 커밋하지 마세요
- S3 버킷은 퍼블릭 액세스를 차단하세요 (Presigned URL 사용)
- IAM 사용자는 최소 권한 원칙을 따르세요

### 카카오 앱 키 발급 (선택)

카카오톡 공유 기능을 사용하려면:

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 로그인 및 앱 생성
3. "내 애플리케이션" → 앱 선택
4. "앱 키" 섹션에서 "JavaScript 키" 복사
5. `.env` 파일에 추가:
   ```bash
   KAKAO_APP_KEY=your-javascript-key
   ```

## 설정 파일 작성

### 1. 결혼 정보 설정 (config.json)

`config/config.json` 파일을 편집하여 실제 결혼 정보를 입력합니다.

**기본 구조:**
```json
{
  "wedding": {
    "groom": {
      "name_kr": "김수환",
      "name_en": "Soohwan",
      "display_name": "수환",
      "birth_order": "장남",
      "parents": {
        "father": "김아버지",
        "mother": "김어머니"
      }
    },
    "bride": {
      "name_kr": "조소영",
      "name_en": "Soyoung",
      "display_name": "소영",
      "birth_order": "장녀",
      "parents": {
        "father": "조아버지",
        "mother": "조어머니"
      }
    },
    "date": {
      "year": 2026,
      "month": 5,
      "day": 17,
      "time": "14:00",
      "day_of_week": "일",
      "display_time": "오후 2시"
    },
    "venue": {
      "name": "라시따시어터",
      "address": "서울특별시 서초구 매헌로 16 1층"
    }
  }
}
```

자세한 설정 방법은 [설정 가이드](./CONFIGURATION.ko.md)를 참고하세요.

### 2. AI 챗봇 지식베이스 작성

`config/couple_knowledge.json` 파일을 편집하여 챗봇이 답변할 내용을 작성합니다.

**최소 예시:**
```json
[
  {
    "id": "first_meeting",
    "topic": "첫 만남",
    "content": "2018년 대학교에서 처음 만났어요."
  },
  {
    "id": "proposal",
    "topic": "프러포즈",
    "content": "2025년 2월에 프로포즈를 했어요."
  },
  {
    "id": "honeymoon",
    "topic": "신혼여행",
    "content": "두바이, 몰디브, 싱가포르로 신혼여행을 갈 예정이에요."
  }
]
```

자세한 작성 방법은 [AI 챗봇 가이드](./CHATBOT.ko.md)를 참고하세요.

### 3. 갤러리 이미지 준비

**이미지 위치:**
```
static/assets/images/wedding-snaps/
```

**이미지 최적화:**
```bash
# 이미지 리사이즈 및 WebP 변환
python scripts/resize_image.py
```

**이미지 규칙:**
- 파일명: `1.webp`, `2.webp`, ... `n.webp`
- 형식: WebP (권장) 또는 JPG
- 크기: 최대 1920px (긴 변 기준)

**config.json에서 개수 설정:**
```json
{
  "content": {
    "gallery": {
      "total_photos": 28
    }
  }
}
```

## 실행 및 테스트

### 1. 데이터베이스 초기화

```bash
# 애플리케이션 실행하면 자동으로 초기화됨
python main.py
```

로그 확인:
```
INFO:     Started server process
INFO:     Waiting for application startup.
✅ guestbook 테이블 확인/생성 완료
✅ rsvp 테이블 확인/생성 완료
🤖 LangGraph chatbot successfully initialized!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. 브라우저에서 접속

**메인 페이지:**
```
http://localhost:8000
```

**관리자 페이지:**
```
http://localhost:8000/admin/login
```

### 3. 기능 테스트

**체크리스트:**

- [ ] 메인 페이지 로딩
- [ ] D-Day 카운터 작동
- [ ] 갤러리 이미지 표시
- [ ] 지도 표시
- [ ] 배경음악 재생
- [ ] AI 챗봇 응답
- [ ] 방명록 작성
- [ ] RSVP 제출
- [ ] 사진 업로드 (AWS S3 연동 시)
- [ ] 관리자 로그인
- [ ] 관리자 대시보드
- [ ] 관리자 사진 관리 (AWS S3 연동 시)

### 4. 개발 모드 실행

코드 변경 시 자동 재시작:

```bash
# --reload 옵션 추가
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 로그 확인

```bash
# 실시간 로그
python main.py

# 또는 개발 모드
uvicorn main:app --reload --log-level debug
```

## 문제 해결

### Python 버전 오류

**증상:**
```
SyntaxError: invalid syntax
```

**해결:**
```bash
# Python 버전 확인
python --version

# 3.8 이상이 아니면 업그레이드
```

### 패키지 설치 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**해결 1: pip 업그레이드**
```bash
pip install --upgrade pip
```

**해결 2: 개별 설치**
```bash
# 문제가 되는 패키지만 설치
pip install fastapi
pip install langchain
```

**해결 3: Python 재설치**
```bash
# 가상환경 삭제 후 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### OpenAI API 오류

**증상:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**해결:**
1. `.env` 파일의 `OPENAI_API_KEY` 확인
2. API 키 앞뒤 공백 제거
3. 따옴표 없이 입력
4. 키가 유효한지 OpenAI 플랫폼에서 확인

### 데이터베이스 오류

**증상:**
```
sqlite3.OperationalError: no such table: guestbook
```

**해결:**
```bash
# 데이터베이스 파일 삭제 후 재생성
rm wedding.db
python main.py
```

### 포트 충돌

**증상:**
```
ERROR: [Errno 48] Address already in use
```

**해결 1: 다른 포트 사용**
```bash
# .env 파일에 추가
PORT=8080

# 또는 직접 지정
python main.py --port 8080
```

**해결 2: 기존 프로세스 종료**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID번호> /F
```

### 환경변수가 로드되지 않음

**증상:**
챗봇이 작동하지 않거나 관리자 로그인 실패

**해결:**
```bash
# .env 파일 위치 확인
ls -la .env

# 파일 내용 확인
cat .env

# python-dotenv 재설치
pip install --upgrade python-dotenv
```

### 가상환경 활성화 문제 (Windows)

**증상:**
```
cannot be loaded because running scripts is disabled on this system
```

**해결:**
```powershell
# PowerShell을 관리자 권한으로 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 CMD 사용
venv\Scripts\activate.bat
```

### 이미지가 표시되지 않음

**증상:**
갤러리가 비어있거나 404 에러

**해결:**
```bash
# 이미지 파일 경로 확인
ls static/assets/images/wedding-snaps/

# config.json에서 개수 확인
# "total_photos": 28 → 실제 이미지 개수와 일치해야 함

# 이미지 권한 확인
chmod 644 static/assets/images/wedding-snaps/*
```

### 챗봇 응답이 없음

**증상:**
챗봇에 질문해도 응답 없음

**해결:**
```bash
# 로그 확인
python main.py

# OpenAI API 키 테스트
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"

# 지식베이스 파일 확인
cat config/couple_knowledge.json
```

## 다음 단계

설치가 완료되었다면:

1. **설정 커스터마이징**
   - [설정 가이드](./CONFIGURATION.ko.md)
   - [챗봇 가이드](./CHATBOT.ko.md)

2. **디자인 수정**
   - [커스터마이징 가이드](./CUSTOMIZATION.ko.md)

3. **배포 준비**
   - [Railway 배포 가이드](./DEPLOYMENT.ko.md)

4. **테스트**
   - 실제 하객들에게 공유 전 충분히 테스트
   - 모바일 기기에서 확인

## 추가 도움말

### 유용한 명령어

**개발 서버 재시작:**
```bash
# Ctrl+C로 종료 후
python main.py
```

**가상환경 비활성화:**
```bash
deactivate
```

**프로젝트 업데이트:**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

**데이터베이스 백업:**
```bash
# SQLite
cp wedding.db wedding.db.backup

# PostgreSQL
pg_dump wedding > backup.sql
```

### 권장 개발 도구

**텍스트 에디터:**
- [Visual Studio Code](https://code.visualstudio.com/) (추천)
- [Sublime Text](https://www.sublimetext.com/)
- [Atom](https://atom.io/)

**VS Code 확장:**
- Python
- Pylance
- SQLite Viewer
- GitLens

**디버깅 도구:**
- Chrome DevTools (F12)
- Python Debugger (pdb)

## 도움이 필요하신가요?

- 📧 [이메일 문의](mailto:your.email@example.com)
- 💬 [디스코드 커뮤니티](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)
- 📖 [FAQ](./FAQ.ko.md)

---

**축하합니다! 🎉**

로컬 환경 설정이 완료되었습니다. 이제 청첩장을 커스터마이징하고 하객들과 공유할 준비가 되었습니다!