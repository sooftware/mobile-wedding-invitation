"""
Admin Authentication Tests
- 관리자 로그인/로그아웃 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.admin
class TestAdminAuth:
    """관리자 인증 테스트"""

    def test_admin_login_page_accessible(self, client: TestClient):
        """로그인 페이지 접근 테스트"""
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert "로그인" in response.text

    def test_admin_login_success(self, client: TestClient):
        """올바른 계정으로 로그인 성공"""
        response = client.post(
            "/admin/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/admin"

    def test_admin_login_wrong_password(self, client: TestClient):
        """잘못된 비밀번호로 로그인 실패"""
        response = client.post(
            "/admin/login",
            data={
                "username": "test_admin",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
        assert "올바르지 않습니다" in response.json()["detail"]

    def test_admin_login_wrong_username(self, client: TestClient):
        """존재하지 않는 사용자명으로 로그인 실패"""
        response = client.post(
            "/admin/login",
            data={
                "username": "wrong_user",
                "password": "admin123"
            }
        )
        assert response.status_code == 401

    def test_admin_dashboard_requires_auth(self, client: TestClient):
        """대시보드는 인증 필요"""
        response = client.get("/admin")
        assert response.status_code == 401

    def test_admin_dashboard_accessible_after_login(self, authenticated_client: TestClient):
        """로그인 후 대시보드 접근 가능"""
        response = authenticated_client.get("/admin")
        assert response.status_code == 200
        assert "관리자 페이지" in response.text

    def test_admin_logout(self, authenticated_client: TestClient):
        """로그아웃 테스트"""
        response = authenticated_client.post("/admin/logout")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 로그아웃 후 대시보드 접근 불가
        response = authenticated_client.get("/admin")
        assert response.status_code == 401


@pytest.mark.admin
class TestAdminSession:
    """관리자 세션 테스트"""

    def test_session_persists_across_requests(self, client: TestClient):
        """세션이 여러 요청에서 유지됨"""
        # 로그인
        client.post(
            "/admin/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            }
        )

        # 첫 번째 요청
        response1 = client.get("/admin")
        assert response1.status_code == 200

        # 두 번째 요청 (같은 세션)
        response2 = client.get("/admin/api/rsvp")
        assert response2.status_code == 200

    def test_session_cleared_after_logout(self, client: TestClient):
        """로그아웃 후 세션 삭제됨"""
        # 로그인
        client.post(
            "/admin/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            }
        )

        # 로그아웃
        client.post("/admin/logout")

        # 대시보드 접근 시도
        response = client.get("/admin")
        assert response.status_code == 401


@pytest.mark.admin
class TestPasswordHashing:
    """비밀번호 해싱 테스트"""

    def test_password_hash_generation(self):
        """비밀번호 해시 생성 테스트"""
        from main import hash_password

        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # 같은 비밀번호는 같은 해시 생성
        assert hash1 == hash2

        # 해시는 64자 (SHA-256)
        assert len(hash1) == 64

    def test_different_passwords_different_hashes(self):
        """다른 비밀번호는 다른 해시 생성"""
        from main import hash_password

        hash1 = hash_password("password1")
        hash2 = hash_password("password2")

        assert hash1 != hash2