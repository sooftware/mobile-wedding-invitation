"""
Pytest Configuration and Fixtures
- 테스트용 공통 설정 및 픽스처

Author: Soohwan Kim (2025.10)
"""

import os
import json
import pytest
import tempfile
import sqlite3
from typing import Generator

# 테스트 환경변수 설정 (실제 .env 파일보다 먼저 설정)
os.environ["DATABASE_URL"] = ""  # SQLite 사용
os.environ["ADMIN_USERNAME"] = "test_admin"
os.environ["ADMIN_PASSWORD_HASH"] = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"  # admin123
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["CHATBOT_ENABLED"] = "false"  # 테스트 시 챗봇 비활성화

# TestClient import는 환경변수 설정 후에
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """테스트 세션 시작 시 DB 초기화"""
    # main 모듈 import 전에 환경변수가 설정되어야 함
    from main import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guestbook (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rsvp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            which_side TEXT NOT NULL,
            can_attend TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            phone_number TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    yield

    # 테스트 종료 후 정리 (선택사항)


@pytest.fixture(scope="session")
def test_db():
    """테스트용 SQLite 데이터베이스"""
    # 실제로는 main.py의 wedding.db를 사용
    yield "wedding.db"


@pytest.fixture(scope="function")
def client():
    """FastAPI 테스트 클라이언트"""
    from main import app
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(client):
    """인증된 관리자 클라이언트"""
    # 로그인
    response = client.post(
        "/admin/login",
        data={
            "username": "test_admin",
            "password": "admin123"
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    return client


@pytest.fixture(scope="function")
def sample_config():
    """샘플 설정 데이터"""
    return {
        "wedding": {
            "groom": {
                "name_kr": "김신랑",
                "name_en": "Kim Groom",
                "display_name": "신랑"
            },
            "bride": {
                "name_kr": "이신부",
                "name_en": "Lee Bride",
                "display_name": "신부"
            },
            "date": {
                "iso_format": "2025-12-25T14:00:00",
                "display_time": "오후 2시"
            },
            "venue": {
                "name": "테스트웨딩홀",
                "address": "서울시 강남구 테스트로 123",
                "full_address": "서울시 강남구 테스트로 123 테스트웨딩홀"
            }
        },
        "content": {
            "chatbot": {
                "welcome": {
                    "greeting": "안녕하세요!",
                    "description": "테스트 챗봇입니다",
                    "suggested_questions": ["질문1", "질문2"]
                },
                "error_message": "오류 발생",
                "thinking_message": "생각중..."
            }
        }
    }


@pytest.fixture(scope="function")
def sample_guestbook_entry():
    """샘플 방명록 데이터"""
    return {
        "name": "테스트유저",
        "message": "축하합니다! 🎉",
        "password": "test1234"
    }


@pytest.fixture(scope="function")
def sample_rsvp_entry():
    """샘플 RSVP 데이터"""
    return {
        "which_side": "신랑측",
        "can_attend": "참석할게요",
        "guest_name": "김하객",
        "phone_number": "010-1234-5678"
    }


@pytest.fixture(scope="function")
def db_connection():
    """데이터베이스 연결 픽스처"""
    from main import get_db_connection
    conn = get_db_connection()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def reset_db(db_connection):
    """각 테스트마다 DB 초기화"""
    cursor = db_connection.cursor()

    # 테이블 초기화
    cursor.execute("DELETE FROM guestbook")
    cursor.execute("DELETE FROM rsvp")

    db_connection.commit()


@pytest.fixture(scope="function")
def mock_chatbot(monkeypatch):
    """Mock 챗봇"""
    class MockChatbot:
        async def get_response(self, query: str):
            return {
                "success": True,
                "response": "테스트 응답입니다.",
                "keywords": ["테스트"],
                "matched_topics": ["테스트"],
                "confidence": 0.9,
                "error": None,
                "retry_count": 0
            }

    def mock_get_chatbot():
        return MockChatbot()

    try:
        from app import chatbot
        monkeypatch.setattr(chatbot, "get_chatbot", mock_get_chatbot)
    except ImportError:
        pass

    yield MockChatbot()


# 테스트 헬퍼 함수들

def create_guestbook_entry(client: TestClient, entry: dict) -> dict:
    """방명록 항목 생성 헬퍼"""
    response = client.post("/api/guestbook", json=entry)
    assert response.status_code == 200
    return response.json()


def create_rsvp_entry(client: TestClient, entry: dict) -> dict:
    """RSVP 항목 생성 헬퍼"""
    response = client.post(
        "/rsvp",
        data={
            "which-side": entry["which_side"],
            "can-attend": entry["can_attend"],
            "guest-name": entry["guest_name"],
            "phone-number": entry.get("phone_number", "")
        },
        follow_redirects=False
    )
    assert response.status_code == 303
    return {"status": "success"}


def login_admin(client: TestClient, username: str = "test_admin", password: str = "admin123"):
    """관리자 로그인 헬퍼"""
    response = client.post(
        "/admin/login",
        data={"username": username, "password": password},
        follow_redirects=False
    )
    return response


# Pytest 플러그인 설정

def pytest_configure(config):
    """Pytest 설정"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """테스트 항목 수정"""
    for item in items:
        # 느린 테스트 자동 마킹
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)