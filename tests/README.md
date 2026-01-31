# 🧪 테스트 가이드

## 📋 목차
1. [테스트 환경 설정](#테스트-환경-설정)
2. [테스트 실행](#테스트-실행)
3. [테스트 구조](#테스트-구조)
4. [커버리지 확인](#커버리지-확인)
5. [CI/CD 통합](#cicd-통합)

---

## 🚀 테스트 환경 설정

### 1. 필수 패키지 설치

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

또는 `tests/requirements.txt` 사용:

```bash
pip install -r tests/requirements.txt
```

### 2. 테스트 환경변수 설정

테스트용 `.env.test` 파일 생성:

```env
ADMIN_USERNAME=test_admin
ADMIN_PASSWORD_HASH=240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
SECRET_KEY=test_secret_key_for_testing_only
OPENAI_API_KEY=test_key
```

---

## 🎯 테스트 실행

### 전체 테스트 실행

```bash
pytest
```

### 특정 마커로 테스트 실행

```bash
# 관리자 테스트만
pytest -m admin

# API 테스트만
pytest -m api

# 단위 테스트만
pytest -m unit

# 통합 테스트만
pytest -m integration
```

### 특정 파일 테스트

```bash
# 방명록 테스트
pytest tests/test_guestbook.py

# 관리자 인증 테스트
pytest tests/test_admin_auth.py
```

### 특정 테스트 클래스/함수

```bash
# 특정 클래스
pytest tests/test_admin_auth.py::TestAdminAuth

# 특정 함수
pytest tests/test_admin_auth.py::TestAdminAuth::test_admin_login_success
```

### Verbose 모드

```bash
pytest -v
pytest -vv  # 더 상세한 출력
```

### 실패한 테스트만 재실행

```bash
pytest --lf  # last-failed
```

---

## 📁 테스트 구조

```
tests/
├── conftest.py              # 공통 fixtures 및 설정
├── test_admin_auth.py       # 관리자 인증 테스트
├── test_admin_api.py        # 관리자 API 테스트
├── test_guestbook.py        # 방명록 기능 테스트
├── test_rsvp.py             # RSVP 기능 테스트
├── test_chatbot.py          # 챗봇 기능 테스트
├── test_database.py         # 데이터베이스 테스트
└── test_main.py             # 메인 라우트 테스트
```

### 테스트 카테고리

| 마커 | 설명 | 예시 |
|------|------|------|
| `unit` | 단위 테스트 | 개별 함수/메서드 테스트 |
| `integration` | 통합 테스트 | 여러 컴포넌트 함께 테스트 |
| `admin` | 관리자 기능 | 로그인, 대시보드, API |
| `api` | API 엔드포인트 | REST API 테스트 |
| `database` | 데이터베이스 | 쿼리, 연결 테스트 |
| `slow` | 느린 테스트 | 챗봇, 외부 API 호출 |

---

## 📊 커버리지 확인

### 커버리지 리포트 생성

```bash
# 터미널에 출력
pytest --cov=app --cov=main

# HTML 리포트 생성
pytest --cov=app --cov=main --cov-report=html

# 브라우저로 열기
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### 커버리지 목표

- **전체 커버리지**: 80% 이상
- **핵심 모듈**: 90% 이상
  - `app/admin/auth.py`
  - `app/database/queries.py`
  - `main.py` (라우트 부분)

### 커버리지가 낮은 부분 확인

```bash
pytest --cov=app --cov-report=term-missing
```

---

## 🔧 유용한 옵션

### 테스트 출력 상세화

```bash
# 표준 출력 보기
pytest -s

# 실패한 테스트의 로컬 변수 보기
pytest -l
```

### 병렬 실행 (빠른 테스트)

```bash
# pytest-xdist 설치 필요
pip install pytest-xdist

# CPU 코어 수만큼 병렬 실행
pytest -n auto
```

### 느린 테스트 제외

```bash
pytest -m "not slow"
```

### 특정 시간 이상 걸리는 테스트 표시

```bash
pytest --durations=10  # 가장 느린 10개 테스트 표시
```

---

## 📝 테스트 작성 가이드

### Fixture 사용 예시

```python
def test_with_client(client: TestClient):
    """클라이언트 fixture 사용"""
    response = client.get("/")
    assert response.status_code == 200

def test_with_auth(authenticated_client: TestClient):
    """인증된 클라이언트 fixture 사용"""
    response = authenticated_client.get("/admin")
    assert response.status_code == 200
```

### 데이터 생성 헬퍼 사용

```python
from tests.conftest import create_guestbook_entry, create_rsvp_entry

def test_with_data(client: TestClient, sample_guestbook_entry: dict):
    # 방명록 생성
    create_guestbook_entry(client, sample_guestbook_entry)
    
    # 테스트 수행
    response = client.get("/api/guestbook")
    assert response.json()["total"] == 1
```

### 마커 사용

```python
@pytest.mark.admin
@pytest.mark.api
def test_admin_api():
    """관리자 API 테스트"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """느린 테스트"""
    pass
```

---

## 🔄 CI/CD 통합

### GitHub Actions 예시

`.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## 🎯 테스트 체크리스트

새로운 기능 추가 시:

- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 에러 케이스 테스트
- [ ] 경계값 테스트
- [ ] 모든 테스트 통과 확인
- [ ] 커버리지 80% 이상 유지

---

## 📊 현재 테스트 통계

```bash
# 전체 테스트 수 확인
pytest --collect-only

# 테스트 실행 통계
pytest --tb=no -q
```

### 테스트 커버리지

| 모듈 | 파일 수 | 테스트 수 | 예상 커버리지 |
|------|---------|-----------|---------------|
| 관리자 | 2 | 25+ | 85%+ |
| 방명록 | 1 | 20+ | 90%+ |
| RSVP | 1 | 15+ | 85%+ |
| 데이터베이스 | 1 | 15+ | 90%+ |
| 메인 | 1 | 15+ | 80%+ |
| **총계** | **7** | **90+** | **85%+** |

---

## 🐛 디버깅 팁

### 특정 테스트 디버깅

```bash
# 실패 시 즉시 중단
pytest -x

# 상세 출력 + 로컬 변수
pytest -vv -l

# PDB 디버거 실행
pytest --pdb
```

### 테스트 로그 보기

```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.INFO):
        # 테스트 수행
        pass
    
    # 로그 확인
    assert "Expected message" in caplog.text
```

---

## 📞 문제 해결

### 문제: ImportError 발생
```bash
# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### 문제: 데이터베이스 에러
```bash
# 테스트 DB 초기화
rm -f wedding.db
pytest
```

### 문제: 세션 관련 에러
```bash
# SECRET_KEY 설정 확인
pytest -v tests/test_admin_auth.py
```

---

## 🎓 더 알아보기

- [Pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI 테스팅](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py 가이드](https://coverage.readthedocs.io/)

---

**Happy Testing! 🧪✨**