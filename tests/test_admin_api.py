"""
Admin API Tests
- 관리자 API 엔드포인트 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import create_guestbook_entry, create_rsvp_entry


@pytest.mark.admin
@pytest.mark.api
class TestAdminRSVPAPI:
    """관리자 RSVP API 테스트"""

    def test_get_rsvp_list_requires_auth(self, client: TestClient):
        """RSVP 목록 조회는 인증 필요"""
        response = client.get("/admin/api/rsvp")
        assert response.status_code == 401

    def test_get_rsvp_list_empty(self, authenticated_client: TestClient):
        """빈 RSVP 목록 조회"""
        response = authenticated_client.get("/admin/api/rsvp")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["entries"] == []

    def test_get_rsvp_list_with_data(
        self,
        client: TestClient,
        authenticated_client: TestClient,
        sample_rsvp_entry: dict
    ):
        """RSVP 데이터가 있을 때 조회"""
        # RSVP 생성
        create_rsvp_entry(client, sample_rsvp_entry)

        # 조회
        response = authenticated_client.get("/admin/api/rsvp")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["entries"]) == 1
        assert data["entries"][0]["guest_name"] == sample_rsvp_entry["guest_name"]

    def test_delete_rsvp_requires_auth(self, client: TestClient):
        """RSVP 삭제는 인증 필요"""
        response = client.delete("/admin/api/rsvp/1")
        assert response.status_code == 401

    def test_delete_rsvp_success(
        self,
        client: TestClient,
        authenticated_client: TestClient,
        sample_rsvp_entry: dict
    ):
        """RSVP 삭제 성공"""
        # RSVP 생성
        create_rsvp_entry(client, sample_rsvp_entry)

        # 목록 조회하여 ID 얻기
        response = authenticated_client.get("/admin/api/rsvp")
        rsvp_id = response.json()["entries"][0]["id"]

        # 삭제
        response = authenticated_client.delete(f"/admin/api/rsvp/{rsvp_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 삭제 확인
        response = authenticated_client.get("/admin/api/rsvp")
        assert response.json()["total"] == 0

    def test_delete_nonexistent_rsvp(self, authenticated_client: TestClient):
        """존재하지 않는 RSVP 삭제 시도"""
        response = authenticated_client.delete("/admin/api/rsvp/99999")
        # SQLite에서는 에러 없이 0 rows affected
        assert response.status_code in [200, 404]


@pytest.mark.admin
@pytest.mark.api
class TestAdminGuestbookAPI:
    """관리자 방명록 API 테스트"""

    def test_delete_guestbook_requires_auth(self, client: TestClient):
        """방명록 삭제는 인증 필요"""
        response = client.delete("/admin/api/guestbook/1")
        assert response.status_code == 401

    def test_delete_guestbook_success(
        self,
        client: TestClient,
        authenticated_client: TestClient,
        sample_guestbook_entry: dict
    ):
        """방명록 삭제 성공"""
        # 방명록 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # 목록 조회하여 ID 얻기
        response = client.get("/api/guestbook")
        guestbook_id = response.json()["entries"][0]["id"]

        # 삭제 (관리자는 비밀번호 불필요)
        response = authenticated_client.delete(f"/admin/api/guestbook/{guestbook_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 삭제 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 0

    def test_admin_can_delete_without_password(
        self,
        client: TestClient,
        authenticated_client: TestClient,
        sample_guestbook_entry: dict
    ):
        """관리자는 비밀번호 없이 방명록 삭제 가능"""
        # 방명록 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        guestbook_id = response.json()["entries"][0]["id"]

        # 일반 사용자는 비밀번호 필요
        import json
        response = client.delete(
            f"/api/guestbook/{guestbook_id}",
            content=json.dumps({
                "id": guestbook_id,
                "password": "wrong_password"
            }),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 403

        # 관리자는 비밀번호 없이 삭제 가능
        response = authenticated_client.delete(f"/admin/api/guestbook/{guestbook_id}")
        assert response.status_code == 200


@pytest.mark.admin
class TestAdminDashboard:
    """관리자 대시보드 테스트"""

    def test_dashboard_shows_statistics(
        self,
        client: TestClient,
        authenticated_client: TestClient,
        sample_guestbook_entry: dict,
        sample_rsvp_entry: dict
    ):
        """대시보드에 통계 표시"""
        # 데이터 생성
        create_guestbook_entry(client, sample_guestbook_entry)
        create_rsvp_entry(client, sample_rsvp_entry)

        # 대시보드 접속
        response = authenticated_client.get("/admin")
        assert response.status_code == 200

        # HTML에 통계 요소 포함 확인
        html = response.text
        assert "total-rsvp" in html
        assert "total-guestbook" in html
        assert "attending-count" in html

    def test_dashboard_has_tabs(self, authenticated_client: TestClient):
        """대시보드에 탭 존재"""
        response = authenticated_client.get("/admin")
        assert response.status_code == 200

        html = response.text
        assert "rsvp-tab" in html
        assert "guestbook-tab" in html

    def test_dashboard_has_csv_export_buttons(self, authenticated_client: TestClient):
        """대시보드에 CSV 내보내기 버튼 존재"""
        response = authenticated_client.get("/admin")
        assert response.status_code == 200

        html = response.text
        assert "exportRSVP" in html or "CSV 다운로드" in html
        assert "exportGuestbook" in html or "CSV 다운로드" in html


@pytest.mark.admin
@pytest.mark.integration
class TestAdminWorkflow:
    """관리자 워크플로우 통합 테스트"""

    def test_complete_admin_workflow(
        self,
        client: TestClient,
        sample_guestbook_entry: dict,
        sample_rsvp_entry: dict
    ):
        """완전한 관리자 워크플로우"""
        # 1. 로그인
        response = client.post(
            "/admin/login",
            data={
                "username": "test_admin",
                "password": "admin123"
            },
            follow_redirects=False
        )
        assert response.status_code == 303

        # 2. 대시보드 접속
        response = client.get("/admin")
        assert response.status_code == 200

        # 3. 데이터 생성
        create_guestbook_entry(client, sample_guestbook_entry)
        create_rsvp_entry(client, sample_rsvp_entry)

        # 4. RSVP 목록 조회
        response = client.get("/admin/api/rsvp")
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # 5. 방명록 조회 (공개 API)
        response = client.get("/api/guestbook")
        assert response.status_code == 200
        assert response.json()["total"] == 1

        # 6. RSVP 삭제
        rsvp_id = client.get("/admin/api/rsvp").json()["entries"][0]["id"]
        response = client.delete(f"/admin/api/rsvp/{rsvp_id}")
        assert response.status_code == 200

        # 7. 방명록 삭제
        gb_id = client.get("/api/guestbook").json()["entries"][0]["id"]
        response = client.delete(f"/admin/api/guestbook/{gb_id}")
        assert response.status_code == 200

        # 8. 로그아웃
        response = client.post("/admin/logout")
        assert response.status_code == 200

        # 9. 로그아웃 후 접근 불가 확인
        response = client.get("/admin")
        assert response.status_code == 401