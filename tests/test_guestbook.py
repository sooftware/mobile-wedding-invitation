"""
Guestbook API Tests
- 방명록 기능 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import create_guestbook_entry


@pytest.mark.api
@pytest.mark.unit
class TestGuestbookAPI:
    """방명록 API 테스트"""

    def test_get_empty_guestbook(self, client: TestClient):
        """빈 방명록 조회"""
        response = client.get("/api/guestbook")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["entries"] == []

    def test_create_guestbook_entry(self, client: TestClient, sample_guestbook_entry: dict):
        """방명록 작성"""
        response = client.post("/api/guestbook", json=sample_guestbook_entry)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_create_guestbook_entry_missing_fields(self, client: TestClient):
        """필수 필드 누락 시 에러"""
        response = client.post("/api/guestbook", json={
            "name": "테스트"
            # message, password 누락
        })
        assert response.status_code == 422

    def test_get_guestbook_with_entries(self, client: TestClient, sample_guestbook_entry: dict):
        """방명록 항목이 있을 때 조회"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # 조회
        response = client.get("/api/guestbook")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["name"] == sample_guestbook_entry["name"]
        assert data["entries"][0]["message"] == sample_guestbook_entry["message"]
        assert "password" not in data["entries"][0]  # 비밀번호는 반환 안 됨


@pytest.mark.api
@pytest.mark.unit
class TestGuestbookUpdate:
    """방명록 수정 테스트"""

    def test_verify_password_correct(self, client: TestClient, sample_guestbook_entry: dict):
        """올바른 비밀번호로 검증 성공"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 비밀번호 검증
        response = client.post(
            f"/api/guestbook/{entry_id}/verify",
            json={
                "id": entry_id,
                "password": sample_guestbook_entry["password"]
            }
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "data" in response.json()
        assert response.json()["data"]["name"] == sample_guestbook_entry["name"]

    def test_verify_password_incorrect(self, client: TestClient, sample_guestbook_entry: dict):
        """잘못된 비밀번호로 검증 실패"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 잘못된 비밀번호로 검증
        response = client.post(
            f"/api/guestbook/{entry_id}/verify",
            json={
                "id": entry_id,
                "password": "wrong_password"
            }
        )
        assert response.status_code == 403

    def test_update_guestbook_entry(self, client: TestClient, sample_guestbook_entry: dict):
        """방명록 수정"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 수정
        updated_data = {
            "id": entry_id,
            "name": "수정된이름",
            "message": "수정된메시지",
            "password": sample_guestbook_entry["password"]
        }
        response = client.put(f"/api/guestbook/{entry_id}", json=updated_data)
        assert response.status_code == 200

        # 수정 확인
        response = client.get("/api/guestbook")
        entry = response.json()["entries"][0]
        assert entry["name"] == "수정된이름"
        assert entry["message"] == "수정된메시지"

    def test_update_with_wrong_password(self, client: TestClient, sample_guestbook_entry: dict):
        """잘못된 비밀번호로 수정 시도"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 잘못된 비밀번호로 수정 시도
        updated_data = {
            "id": entry_id,
            "name": "수정된이름",
            "message": "수정된메시지",
            "password": "wrong_password"
        }
        response = client.put(f"/api/guestbook/{entry_id}", json=updated_data)
        assert response.status_code == 403


@pytest.mark.api
@pytest.mark.unit
class TestGuestbookDelete:
    """방명록 삭제 테스트"""

    def test_delete_guestbook_entry(self, client: TestClient, sample_guestbook_entry: dict):
        """방명록 삭제"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 삭제
        import json
        response = client.delete(
            f"/api/guestbook/{entry_id}",
            content=json.dumps({
                "id": entry_id,
                "password": sample_guestbook_entry["password"]
            }),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200

        # 삭제 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 0

    def test_delete_with_wrong_password(self, client: TestClient, sample_guestbook_entry: dict):
        """잘못된 비밀번호로 삭제 시도"""
        # 생성
        create_guestbook_entry(client, sample_guestbook_entry)

        # ID 얻기
        response = client.get("/api/guestbook")
        entry_id = response.json()["entries"][0]["id"]

        # 잘못된 비밀번호로 삭제
        import json
        response = client.delete(
            f"/api/guestbook/{entry_id}",
            content=json.dumps({
                "id": entry_id,
                "password": "wrong_password"
            }),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 403

        # 삭제되지 않았는지 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 1

    def test_delete_nonexistent_entry(self, client: TestClient):
        """존재하지 않는 항목 삭제 시도"""
        import json
        response = client.delete(
            "/api/guestbook/99999",
            content=json.dumps({
                "id": 99999,
                "password": "any_password"
            }),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestGuestbookWorkflow:
    """방명록 워크플로우 통합 테스트"""

    def test_complete_guestbook_workflow(self, client: TestClient):
        """완전한 방명록 워크플로우"""
        # 1. 초기 상태 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 0

        # 2. 방명록 작성
        entry = {
            "name": "김하객",
            "message": "축하합니다!",
            "password": "test1234"
        }
        response = client.post("/api/guestbook", json=entry)
        assert response.status_code == 200

        # 3. 작성 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 1
        entry_id = response.json()["entries"][0]["id"]

        # 4. 비밀번호 검증
        response = client.post(
            f"/api/guestbook/{entry_id}/verify",
            json={"id": entry_id, "password": "test1234"}
        )
        assert response.status_code == 200

        # 5. 수정
        response = client.put(
            f"/api/guestbook/{entry_id}",
            json={
                "id": entry_id,
                "name": "김하객(수정)",
                "message": "축하합니다! (수정)",
                "password": "test1234"
            }
        )
        assert response.status_code == 200

        # 6. 수정 확인
        response = client.get("/api/guestbook")
        entry = response.json()["entries"][0]
        assert "(수정)" in entry["name"]

        # 7. 삭제
        import json
        response = client.delete(
            f"/api/guestbook/{entry_id}",
            content=json.dumps({"id": entry_id, "password": "test1234"}),
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200

        # 8. 삭제 확인
        response = client.get("/api/guestbook")
        assert response.json()["total"] == 0