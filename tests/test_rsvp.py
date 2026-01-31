"""
RSVP API Tests
- RSVP 기능 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import create_rsvp_entry


@pytest.mark.api
@pytest.mark.unit
class TestRSVPSubmission:
    """RSVP 제출 테스트"""

    def test_submit_rsvp_form(self, client: TestClient, sample_rsvp_entry: dict):
        """RSVP 폼 제출"""
        response = client.post(
            "/rsvp",
            data={
                "which-side": sample_rsvp_entry["which_side"],
                "can-attend": sample_rsvp_entry["can_attend"],
                "guest-name": sample_rsvp_entry["guest_name"],
                "phone-number": sample_rsvp_entry["phone_number"]
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/thanks"

    def test_submit_rsvp_without_phone(self, client: TestClient):
        """연락처 없이 RSVP 제출"""
        response = client.post(
            "/rsvp",
            data={
                "which-side": "신랑측",
                "can-attend": "참석할게요",
                "guest-name": "김하객",
                "phone-number": ""  # 빈 문자열
            },
            follow_redirects=False
        )
        assert response.status_code == 303

    def test_submit_rsvp_missing_required_fields(self, client: TestClient):
        """필수 필드 누락"""
        response = client.post(
            "/rsvp",
            data={
                "which-side": "신랑측"
                # can-attend, guest-name 누락
            },
            follow_redirects=False
        )
        assert response.status_code == 422

    def test_rsvp_form_page_accessible(self, client: TestClient):
        """RSVP 폼 페이지 접근"""
        response = client.get("/rsvp-form")
        assert response.status_code == 200
        assert "RSVP" in response.text or "참석" in response.text

    def test_rsvp_thanks_page_accessible(self, client: TestClient):
        """RSVP 감사 페이지 접근"""
        response = client.get("/thanks")
        assert response.status_code == 200
        assert "감사" in response.text or "thank" in response.text.lower()


@pytest.mark.api
@pytest.mark.integration
class TestRSVPData:
    """RSVP 데이터 테스트"""

    def test_rsvp_data_persists(self, client: TestClient, sample_rsvp_entry: dict):
        """RSVP 데이터가 저장됨"""
        # 제출
        create_rsvp_entry(client, sample_rsvp_entry)

        # 로그인 후 조회
        client.post(
            "/admin/login",
            data={"username": "test_admin", "password": "admin123"}
        )
        response = client.get("/admin/api/rsvp")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        entry = data["entries"][0]
        assert entry["which_side"] == sample_rsvp_entry["which_side"]
        assert entry["can_attend"] == sample_rsvp_entry["can_attend"]
        assert entry["guest_name"] == sample_rsvp_entry["guest_name"]

    def test_multiple_rsvp_submissions(self, client: TestClient):
        """여러 RSVP 제출"""
        entries = [
            {
                "which_side": "신랑측",
                "can_attend": "참석할게요",
                "guest_name": "김하객1",
                "phone_number": "010-1111-1111"
            },
            {
                "which_side": "신부측",
                "can_attend": "참석이 어려워요",
                "guest_name": "이하객2",
                "phone_number": "010-2222-2222"
            },
            {
                "which_side": "신랑측",
                "can_attend": "고민중이에요",
                "guest_name": "박하객3",
                "phone_number": ""
            }
        ]

        for entry in entries:
            create_rsvp_entry(client, entry)

        # 확인
        client.post(
            "/admin/login",
            data={"username": "test_admin", "password": "admin123"}
        )
        response = client.get("/admin/api/rsvp")
        assert response.json()["total"] == 3


@pytest.mark.integration
class TestRSVPWorkflow:
    """RSVP 워크플로우 통합 테스트"""

    def test_complete_rsvp_workflow(self, client: TestClient):
        """완전한 RSVP 워크플로우"""
        # 1. RSVP 폼 페이지 접속
        response = client.get("/rsvp-form")
        assert response.status_code == 200

        # 2. RSVP 제출
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

        # 3. 감사 페이지로 리다이렉트 확인
        response = client.get("/thanks")
        assert response.status_code == 200

        # 4. 관리자 로그인
        response = client.post(
            "/admin/login",
            data={"username": "test_admin", "password": "admin123"},
            follow_redirects=False
        )
        # 303 또는 200 (자동 follow된 경우)
        assert response.status_code in [200, 303]

        # 5. 관리자 페이지에서 RSVP 확인
        response = client.get("/admin/api/rsvp")
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # 6. RSVP 삭제
        entry_id = response.json()["entries"][0]["id"]
        response = client.delete(f"/admin/api/rsvp/{entry_id}")
        assert response.status_code == 200

        # 7. 삭제 확인
        response = client.get("/admin/api/rsvp")
        assert response.json()["total"] == 0


@pytest.mark.unit
class TestRSVPValidation:
    """RSVP 유효성 검사 테스트"""

    def test_valid_which_side_values(self, client: TestClient):
        """유효한 which_side 값들"""
        valid_sides = ["신랑측", "신부측"]

        for side in valid_sides:
            response = client.post(
                "/rsvp",
                data={
                    "which-side": side,
                    "can-attend": "참석할게요",
                    "guest-name": "테스트",
                    "phone-number": "010-1234-5678"
                },
                follow_redirects=False
            )
            assert response.status_code == 303

    def test_valid_can_attend_values(self, client: TestClient):
        """유효한 can_attend 값들"""
        valid_statuses = ["참석할게요", "참석이 어려워요", "고민중이에요"]

        for status in valid_statuses:
            response = client.post(
                "/rsvp",
                data={
                    "which-side": "신랑측",
                    "can-attend": status,
                    "guest-name": "테스트",
                    "phone-number": "010-1234-5678"
                },
                follow_redirects=False
            )
            assert response.status_code == 303