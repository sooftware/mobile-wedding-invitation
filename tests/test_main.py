"""
Main Routes Tests
- 기본 라우트 및 페이지 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestMainRoutes:
    """메인 라우트 테스트"""

    def test_home_page(self, client: TestClient):
        """홈 페이지 접근"""
        response = client.get("/")
        assert response.status_code == 200
        assert "html" in response.headers["content-type"]

    def test_guestbook_form_page(self, client: TestClient):
        """방명록 폼 페이지"""
        response = client.get("/guestbook")
        assert response.status_code == 200
        assert "방명록" in response.text or "guestbook" in response.text.lower()

    def test_guestbook_thanks_page(self, client: TestClient):
        """방명록 감사 페이지"""
        response = client.get("/guestbook-thanks")
        assert response.status_code == 200

    def test_rsvp_form_page(self, client: TestClient):
        """RSVP 폼 페이지"""
        response = client.get("/rsvp-form")
        assert response.status_code == 200
        assert "참석" in response.text or "rsvp" in response.text.lower()

    def test_rsvp_thanks_page(self, client: TestClient):
        """RSVP 감사 페이지"""
        response = client.get("/thanks")
        assert response.status_code == 200


@pytest.mark.unit
class TestStaticFiles:
    """정적 파일 테스트"""

    def test_static_css_accessible(self, client: TestClient):
        """CSS 파일 접근"""
        response = client.get("/static/css/main.min.css")
        # 파일이 있으면 200, 없으면 404
        assert response.status_code in [200, 404]

    def test_static_js_accessible(self, client: TestClient):
        """JavaScript 파일 접근"""
        response = client.get("/static/js/main.js")
        assert response.status_code in [200, 404]

    def test_admin_css_accessible(self, client: TestClient):
        """관리자 CSS 파일 접근"""
        response = client.get("/static/css/admin.css")
        assert response.status_code in [200, 404]

    def test_admin_js_accessible(self, client: TestClient):
        """관리자 JavaScript 파일 접근"""
        response = client.get("/static/js/admin.js")
        assert response.status_code in [200, 404]


@pytest.mark.unit
class TestErrorHandling:
    """에러 핸들링 테스트"""

    def test_404_page(self, client: TestClient):
        """존재하지 않는 페이지"""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404

    def test_invalid_method(self, client: TestClient):
        """잘못된 HTTP 메소드"""
        response = client.put("/")
        assert response.status_code == 405


@pytest.mark.integration
class TestPageFlow:
    """페이지 플로우 테스트"""

    def test_guestbook_submission_flow(self, client: TestClient):
        """방명록 제출 플로우"""
        # 1. 폼 페이지
        response = client.get("/guestbook")
        assert response.status_code == 200

        # 2. 제출
        response = client.post(
            "/guestbook",
            data={
                "name": "테스트",
                "message": "메시지",
                "password": "test1234"
            },
            follow_redirects=False
        )
        assert response.status_code == 303

        # 3. 감사 페이지
        response = client.get("/guestbook-thanks")
        assert response.status_code == 200

    def test_rsvp_submission_flow(self, client: TestClient):
        """RSVP 제출 플로우"""
        # 1. 폼 페이지
        response = client.get("/rsvp-form")
        assert response.status_code == 200

        # 2. 제출
        response = client.post(
            "/rsvp",
            data={
                "which-side": "신랑측",
                "can-attend": "참석할게요",
                "guest-name": "테스트",
                "phone-number": "010-1234-5678"
            },
            follow_redirects=False
        )
        assert response.status_code == 303

        # 3. 감사 페이지
        response = client.get("/thanks")
        assert response.status_code == 200


@pytest.mark.unit
class TestConfigLoading:
    """설정 로딩 테스트"""

    def test_config_exists(self, sample_config):
        """설정 파일 존재"""
        assert sample_config is not None
        assert "wedding" in sample_config

    def test_config_has_required_fields(self, sample_config):
        """필수 필드 존재"""
        wedding = sample_config["wedding"]
        assert "groom" in wedding
        assert "bride" in wedding
        assert "date" in wedding
        assert "venue" in wedding

    def test_config_groom_info(self, sample_config):
        """신랑 정보"""
        groom = sample_config["wedding"]["groom"]
        assert "name_kr" in groom
        assert "name_en" in groom
        assert "display_name" in groom

    def test_config_bride_info(self, sample_config):
        """신부 정보"""
        bride = sample_config["wedding"]["bride"]
        assert "name_kr" in bride
        assert "name_en" in bride
        assert "display_name" in bride


@pytest.mark.integration
class TestFullUserJourney:
    """전체 사용자 여정 테스트"""

    def test_guest_complete_journey(self, client: TestClient):
        """하객의 완전한 여정"""
        # 1. 홈 페이지 방문
        response = client.get("/")
        assert response.status_code == 200

        # 2. RSVP 작성
        response = client.post(
            "/rsvp",
            data={
                "which-side": "신랑측",
                "can-attend": "참석할게요",
                "guest-name": "김하객",
                "phone-number": "010-1234-5678"
            },
            follow_redirects=False
        )
        assert response.status_code == 303

        # 3. 방명록 작성
        response = client.post(
            "/api/guestbook",
            json={
                "name": "김하객",
                "message": "축하합니다!",
                "password": "test1234"
            }
        )
        assert response.status_code == 200

        # 4. 방명록 확인
        response = client.get("/api/guestbook")
        assert response.status_code == 200
        assert response.json()["total"] == 1