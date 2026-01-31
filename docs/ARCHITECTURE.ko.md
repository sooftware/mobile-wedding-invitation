# 🏗️ System Architecture

[English](./ARCHITECTURE.md) | **한국어**

이 문서는 AI 결혼 청첩장 프로젝트의 시스템 아키텍처와 설계 결정 사항을 설명합니다.

## 📋 목차

- [전체 아키텍처](#전체-아키텍처)
- [백엔드 구조](#백엔드-구조)
- [AI 챗봇 아키텍처](#ai-챗봇-아키텍처)
- [데이터베이스 설계](#데이터베이스-설계)
- [프론트엔드 구조](#프론트엔드-구조)
- [배포 아키텍처](#배포-아키텍처)
- [보안 설계](#보안-설계)
- [성능 최적화](#성능-최적화)

## 전체 아키텍처

### 시스템 개요

```
┌─────────────────────────────────────────────────────────────┐
│                         사용자 (하객)                          │
│                    브라우저 / 모바일 기기                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Railway Platform                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                      │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │   Static   │  │   Templates  │  │     API     │ │  │
│  │  │   Files    │  │   (Jinja2)   │  │  Endpoints  │ │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘ │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │          LangGraph AI Chatbot                  │ │  │
│  │  │  ┌──────────┐  ┌───────────┐  ┌────────────┐ │ │  │
│  │  │  │ Keyword  │→ │  Vector   │→ │  Response  │ │ │  │
│  │  │  │Extraction│  │  Search   │  │ Generation │ │ │  │
│  │  │  └──────────┘  └───────────┘  └────────────┘ │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │                          │                           │  │
│  │                          ▼                           │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │              Session Management                 │ │  │
│  │  │          (관리자 인증 / CSRF 보호)               │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │Guestbook │  │   RSVP   │  │  Admin Sessions  │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  OpenAI API  │  │  Chroma DB   │  │  LangSmith (옵션)│ │
│  │   (GPT-4)    │  │   (Vector)   │  │    (Tracing)     │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AWS S3 (Object Storage)                  │  │
│  │         - 사진 업로드 저장                             │  │
│  │         - Presigned URL 제공                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 주요 구성 요소

**1. 웹 서버 (FastAPI)**
- 비동기 요청 처리
- RESTful API 제공
- 정적 파일 서빙
- 템플릿 렌더링

**2. AI 챗봇 (LangGraph)**
- 상태 관리 워크플로우
- RAG 기반 지식 검색
- 재시도 로직

**3. 데이터베이스 (PostgreSQL/SQLite)**
- 방명록 저장
- RSVP 관리
- 세션 저장

**4. 외부 서비스**
- OpenAI: LLM 추론
- Chroma: 벡터 검색
- AWS S3: 사진 스토리지
- LangSmith: 추적 (선택)

## 백엔드 구조

### 디렉토리 구조

```
app/
├── chatbot/              # AI 챗봇 모듈
│   ├── __init__.py
│   ├── chatbot.py       # LangGraph 챗봇 구현
│   └── schemas.py       # Pydantic 스키마
├── core/                # 핵심 모듈
│   ├── __init__.py
│   ├── config.py        # 설정 관리
│   ├── database.py      # DB 연결
│   ├── storage.py       # AWS S3 스토리지
│   └── chatbot_init.py  # 챗봇 초기화
├── database/            # 데이터베이스 레이어
│   ├── __init__.py
│   └── queries.py       # SQL 쿼리 함수
├── routers/             # API 라우터
│   ├── __init__.py
│   ├── home.py          # 메인 페이지
│   ├── chatbot.py       # 챗봇 API
│   ├── guestbook.py     # 방명록 API
│   ├── rsvp.py          # RSVP API
│   ├── photos.py        # 사진 업로드 API
│   ├── stats.py         # 통계 API
│   └── admin.py         # 관리자 API
├── admin/               # 관리자 기능
│   ├── __init__.py
│   └── auth.py          # 인증 & 세션
├── models.py            # 데이터 모델
└── __init__.py
```

### 레이어 아키텍처

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│   (FastAPI Routes / Templates)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│  (Chatbot / Admin Auth / Validation)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Data Access Layer              │
│        (Database Queries)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           Database Layer                │
│     (PostgreSQL / SQLite)               │
└─────────────────────────────────────────┘
```

### 주요 엔드포인트

**공개 API:**
```python
GET  /                    # 메인 페이지
GET  /guestbook          # 방명록 페이지
POST /guestbook          # 방명록 작성
PUT  /guestbook/{id}     # 방명록 수정
DELETE /guestbook/{id}   # 방명록 삭제
GET  /api/guestbook      # 방명록 조회
POST /rsvp               # RSVP 제출
POST /chat               # AI 챗봇 대화
POST /photos/upload      # 사진 업로드 (최대 50장)
```

**관리자 API:**
```python
GET  /admin/login            # 로그인 페이지
POST /admin/login            # 로그인 처리
GET  /admin                  # 관리자 대시보드
GET  /admin/guestbook        # 방명록 관리
GET  /admin/rsvp             # RSVP 관리
GET  /admin/rsvp/export      # RSVP CSV 내보내기
GET  /photos/api/list        # 사진 목록 조회
GET  /photos/api/list-s3     # S3 사진 목록 직접 조회
DELETE /photos/api/{id}      # 사진 삭제
GET  /photos/api/download/{id}  # 사진 다운로드
GET  /photos/api/stats       # 사진 통계
POST /admin/logout           # 로그아웃
```

## AI 챗봇 아키텍처

### LangGraph 워크플로우

```
사용자 입력
    │
    ▼
┌────────────────────────┐
│  키워드 추출 노드       │
│  (Keyword Extraction)  │
│  - LLM으로 핵심 키워드 추출
│  - 검색 쿼리 생성       │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  문서 검색 노드         │
│  (Document Retrieval)  │
│  - Chroma 벡터 검색    │
│  - 유사도 기반 정렬     │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  신뢰도 계산 노드       │
│  (Confidence Check)    │
│  - 검색 결과 개수 확인  │
│  - 신뢰도 점수 계산     │
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   신뢰도 높음   신뢰도 낮음
      │           │
      ▼           ▼
┌────────────┐ ┌────────────┐
│ 답변 생성   │ │  Fallback  │
│  (LLM)     │ │  메시지    │
└─────┬──────┘ └──────┬─────┘
      │               │
      └───────┬───────┘
              ▼
         최종 응답
```

### 상태 관리

```python
class ChatbotState(TypedDict):
    """챗봇 상태"""
    question: str              # 사용자 질문
    keywords: List[str]        # 추출된 키워드
    documents: List[Document]  # 검색된 문서
    confidence: float          # 신뢰도 점수
    should_fallback: bool      # Fallback 여부
    response: str              # 최종 응답
    iterations: int            # 반복 횟수 (무한루프 방지)
```

### RAG (Retrieval-Augmented Generation)

**1. 지식베이스 구축**
```python
# couple_knowledge.json → Chroma Vector Store
knowledge = load_json("config/couple_knowledge.json")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=knowledge,
    embedding=embeddings
)
```

**2. 검색 (Retrieval)**
```python
# 키워드 기반 벡터 검색
results = vectorstore.similarity_search(
    query=keywords,
    k=TOP_K_RESULTS  # 기본값: 3
)
```

**3. 생성 (Generation)**
```python
# 검색된 컨텍스트로 답변 생성
response = llm.invoke(
    f"컨텍스트: {context}\n질문: {question}"
)
```

### 재시도 및 오류 처리

```python
# Exponential Backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        response = llm.invoke(prompt)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)
        else:
            return fallback_message
```

## 데이터베이스 설계

### ERD (Entity-Relationship Diagram)

```
┌─────────────────────┐
│     guestbook       │
├─────────────────────┤
│ id (PK)             │
│ guest_name          │
│ message             │
│ password_hash       │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│        rsvp         │
├─────────────────────┤
│ id (PK)             │
│ guest_name          │
│ which_side          │ ← 신랑측/신부측
│ can_attend          │ ← 참석/불참
│ phone_last_digits   │ ← 동명이인 구분
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│       photos        │
├─────────────────────┤
│ id (PK)             │
│ filename            │
│ file_path           │ ← S3 경로
│ file_size           │
│ content_type        │
│ uploader_name       │
│ timestamp           │
└─────────────────────┘

┌─────────────────────┐
│   admin_sessions    │
├─────────────────────┤
│ session_id (PK)     │
│ username            │
│ created_at          │
│ expires_at          │
└─────────────────────┘
```

### 테이블 상세

**guestbook 테이블**
```sql
CREATE TABLE guestbook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    message TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**rsvp 테이블**
```sql
CREATE TABLE rsvp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    which_side TEXT NOT NULL,  -- '신랑' 또는 '신부'
    can_attend TEXT NOT NULL,  -- '참석할게요' 또는 '아쉽지만 불참할게요'
    phone_last_digits TEXT,    -- 선택, 동명이인 구분용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**photos 테이블**
```sql
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,        -- S3 경로
    file_size INTEGER NOT NULL,      -- 바이트 단위
    content_type TEXT,               -- MIME type (예: image/jpeg)
    uploader_name TEXT,              -- 업로드한 사람 이름 (선택)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**admin_sessions 테이블**
```sql
CREATE TABLE admin_sessions (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

### 인덱스

```sql
-- 성능 최적화를 위한 인덱스
CREATE INDEX idx_guestbook_created_at ON guestbook(created_at DESC);
CREATE INDEX idx_rsvp_which_side ON rsvp(which_side);
CREATE INDEX idx_rsvp_can_attend ON rsvp(can_attend);
CREATE INDEX idx_photos_timestamp ON photos(timestamp DESC);
CREATE INDEX idx_admin_sessions_expires_at ON admin_sessions(expires_at);
```

## 프론트엔드 구조

### 파일 구조

```
static/
├── css/
│   ├── variables.css    # CSS 변수 (색상, 폰트)
│   ├── reset.css        # CSS 리셋
│   ├── main.css         # 메인 스타일
│   ├── animations.css   # 애니메이션
│   └── admin.css        # 관리자 페이지 스타일
├── js/
│   ├── main.js          # 메인 로직
│   ├── chatbot.js       # 챗봇 UI
│   ├── guestbook.js     # 방명록 UI
│   ├── rsvp.js          # RSVP UI
│   ├── animations.js    # 꽃잎 애니메이션
│   └── admin.js         # 관리자 기능
└── assets/
    ├── images/          # 이미지 파일
    ├── audio/           # 배경음악
    └── icons/           # 아이콘

templates/
├── index.html           # 메인 페이지
├── guestbook.html       # 방명록 작성 페이지
└── admin.html           # 관리자 대시보드
```

### JavaScript 모듈

**main.js** - 페이지 초기화
```javascript
// D-Day 계산
// 배경음악 제어
// 스크롤 애니메이션
// 공유 기능
```

**chatbot.js** - 챗봇 인터페이스
```javascript
// 메시지 전송
// 응답 렌더링
// 추천 질문 처리
```

**guestbook.js** - 방명록 CRUD
```javascript
// 방명록 조회
// 메시지 작성/수정/삭제
// 페이지네이션
```

**animations.js** - 꽃잎 애니메이션
```javascript
// 자연스러운 낙하 물리
// 성능 최적화
// 반응형 처리
```

### CSS 아키텍처

**CSS 변수 (Design Tokens)**
```css
:root {
  /* Colors */
  --primary-color: #B59493;
  --background-color: #FFFFFF;
  --text-primary: #333333;
  
  /* Typography */
  --font-family-main: 'Noto Sans KR', sans-serif;
  --font-size-base: 16px;
  
  /* Spacing */
  --spacing-sm: 10px;
  --spacing-md: 20px;
  --spacing-lg: 40px;
  
  /* Layout */
  --max-width: 800px;
  --section-spacing: 80px;
}
```

**BEM 방법론**
```css
/* Block */
.chatbot { }

/* Element */
.chatbot__message { }
.chatbot__input { }

/* Modifier */
.chatbot__message--user { }
.chatbot__message--bot { }
```

## 배포 아키텍처

### Railway 배포

```
┌─────────────────────────────────────────────┐
│           GitHub Repository                  │
│  (main branch에 push → 자동 배포)            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Railway Build Process                │
│  1. Detect Python                            │
│  2. Install dependencies (requirements.txt)  │
│  3. Run main.py                              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│        Railway Runtime Environment           │
│  ┌──────────────────────────────────────┐  │
│  │  FastAPI Application (uvicorn)       │  │
│  │  Port: $PORT (auto-assigned)         │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  PostgreSQL Database                 │  │
│  │  DATABASE_URL (auto-configured)      │  │
│  └──────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Railway Edge Network                 │
│  - HTTPS 자동 적용                           │
│  - 커스텀 도메인 지원                         │
│  - DDoS 보호                                 │
└─────────────────────────────────────────────┘
```

### 환경 분리

**개발 환경 (로컬)**
```bash
DATABASE_URL=sqlite:///wedding.db
DEBUG=true
LOG_LEVEL=debug
```

**프로덕션 환경 (Railway)**
```bash
DATABASE_URL=postgresql://... (자동 설정)
DEBUG=false
LOG_LEVEL=info
```

## 보안 설계

### 인증 및 권한

**관리자 인증 플로우**
```
1. 사용자가 /admin/login에 접속
2. username + password 입력
3. 서버에서 password_hash 검증
4. 검증 성공 시 세션 생성
5. 세션 ID를 쿠키로 전송
6. 이후 요청 시 세션 ID 검증
```

**세션 관리**
```python
# 세션 생성
session_id = secrets.token_urlsafe(32)
expires_at = datetime.now() + timedelta(hours=24)

# 세션 검증
def verify_session(session_id: str) -> bool:
    session = get_session(session_id)
    if not session:
        return False
    if session.expires_at < datetime.now():
        delete_session(session_id)
        return False
    return True
```

### 비밀번호 보호

**방명록 비밀번호**
```python
import hashlib

# 저장
password_hash = hashlib.sha256(
    password.encode()
).hexdigest()

# 검증
input_hash = hashlib.sha256(
    input_password.encode()
).hexdigest()
is_valid = input_hash == stored_hash
```

**관리자 비밀번호**
```python
# 스크립트로 미리 해시 생성
python scripts/generate_password_hash.py

# .env에 저장
ADMIN_PASSWORD_HASH=a665a4592042...
```

### 입력 검증

**Pydantic 스키마**
```python
from pydantic import BaseModel, validator

class GuestbookEntry(BaseModel):
    guest_name: str
    message: str
    password: str
    
    @validator('guest_name')
    def name_length(cls, v):
        if len(v) > 50:
            raise ValueError('이름은 50자 이하')
        return v
    
    @validator('message')
    def message_length(cls, v):
        if len(v) > 500:
            raise ValueError('메시지는 500자 이하')
        return v
```

### HTTPS 및 CORS

**HTTPS**
- Railway가 자동으로 Let's Encrypt SSL 인증서 발급
- 모든 HTTP 요청을 HTTPS로 리다이렉트

**CORS**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 성능 최적화

### 백엔드 최적화

**비동기 처리**
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # 비동기로 LLM 호출
    response = await chatbot.ainvoke(request.message)
    return response
```

**데이터베이스 커넥션 풀링**
```python
# SQLAlchemy 엔진 설정
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # 최대 5개 커넥션
    max_overflow=10,    # 추가 10개까지 허용
    pool_pre_ping=True  # 커넥션 유효성 검사
)
```

### 프론트엔드 최적화

**이미지 최적화**
```bash
# WebP 변환 (60-80% 용량 감소)
python scripts/resize_image.py

# 레이지 로딩
<img loading="lazy" src="...">
```

**CSS/JS 최적화**
```html
<!-- CSS 먼저 로드 -->
<link rel="stylesheet" href="/static/css/main.css">

<!-- JS는 defer로 로드 -->
<script defer src="/static/js/main.js"></script>
```

**캐싱 전략**
```python
# 정적 파일 캐싱 (1년)
@app.get("/static/{path:path}")
async def static_files(path: str):
    return FileResponse(
        f"static/{path}",
        headers={
            "Cache-Control": "public, max-age=31536000"
        }
    )
```

### AI 챗봇 최적화

**벡터 검색 최적화**
```python
# TOP_K 조정 (많을수록 정확하지만 느림)
TOP_K_RESULTS = 3  # 기본값

# 임베딩 캐싱
@lru_cache(maxsize=100)
def get_embeddings(text: str):
    return embeddings.embed_query(text)
```

**LLM 호출 최적화**
```python
# 토큰 수 제한
MAX_TOKENS = 300  # 응답 길이 제한

# Temperature 낮춰서 빠르게
CHAT_TEMPERATURE = 0.3

# 저렴한 모델 사용
CHAT_MODEL = "gpt-4o-mini"  # gpt-4 대신
```

## 모니터링 및 로깅

### 로깅 전략

```python
import logging

# 개발 환경
logging.basicConfig(level=logging.DEBUG)

# 프로덕션 환경
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 챗봇 로깅
logger.info(f"Question: {question}")
logger.info(f"Response: {response}")
logger.error(f"Error: {error}")
```

### LangSmith 추적 (선택)

```python
# .env 설정
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGSMITH_PROJECT=wedding-chatbot

# 자동으로 모든 LLM 호출 추적
# 대시보드에서 확인:
# - 각 단계별 실행 시간
# - 입력/출력 내용
# - 비용 계산
```

## 확장 가능성

### 수평 확장

```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌────┐  ┌────┐
│App1│  │App2│  ← Stateless 애플리케이션
└─┬──┘  └─┬──┘
  │       │
  └───┬───┘
      ▼
┌──────────┐
│Shared DB │
└──────────┘
```

### 기능 확장

**추가 가능한 기능:**
- 실시간 알림 (WebSocket)
- 이미지 업로드 (S3/CloudFlare)
- 이메일 알림 (SendGrid)
- 다국어 지원 (i18n)
- A/B 테스트
- 분석 대시보드

## 기술적 결정 사항

### 왜 FastAPI?

✅ **장점:**
- 빠른 성능 (Starlette 기반)
- 비동기 지원
- 자동 API 문서 (Swagger)
- Pydantic 통합

### 왜 LangGraph?

✅ **장점:**
- 상태 관리 용이
- 복잡한 워크플로우 구현
- 디버깅 편리
- LangSmith 통합

### 왜 SQLite/PostgreSQL?

✅ **SQLite (개발):**
- 설정 불필요
- 파일 기반
- 빠른 프로토타이핑

✅ **PostgreSQL (프로덕션):**
- 동시성 지원
- 안정성
- Railway 통합

### 왜 Vanilla JS?

✅ **장점:**
- 빠른 로딩
- 작은 번들 크기
- 프레임워크 오버헤드 없음
- 간단한 프로젝트에 적합

## 참고 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [LangChain 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Railway 문서](https://docs.railway.app/)

---

**Last Updated**: 2025-01-22  
**Version**: 1.0.0