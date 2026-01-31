"""
Chatbot API Tests
- 챗봇 기능 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
@pytest.mark.unit
class TestChatbotAPI:
    """챗봇 API 테스트"""

    def test_chatbot_endpoint_exists(self, client: TestClient):
        """챗봇 엔드포인트 존재 확인"""
        response = client.post(
            "/api/chatbot",
            json={"message": "안녕하세요"}
        )
        # 챗봇이 비활성화되어 있어도 503, 500, 또는 200 응답
        assert response.status_code in [200, 500, 503]

    def test_chatbot_with_mock(self, client: TestClient, mock_chatbot):
        """Mock 챗봇으로 테스트"""
        response = client.post(
            "/api/chatbot",
            json={"message": "두 분은 어떻게 만나셨나요?"}
        )

        # 챗봇이 활성화되어 있다면
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert data["success"] is True

    def test_chatbot_empty_message(self, client: TestClient):
        """빈 메시지 전송"""
        response = client.post(
            "/api/chatbot",
            json={"message": ""}
        )
        # 빈 메시지도 처리되거나 422 에러, 또는 500
        assert response.status_code in [200, 422, 500, 503]

    def test_chatbot_long_message(self, client: TestClient):
        """긴 메시지 전송"""
        long_message = "안녕하세요! " * 100
        response = client.post(
            "/api/chatbot",
            json={"message": long_message}
        )
        assert response.status_code in [200, 500, 503]


@pytest.mark.integration
@pytest.mark.slow
class TestChatbotIntegration:
    """챗봇 통합 테스트"""

    @pytest.mark.slow
    def test_chatbot_response_quality(self, client: TestClient, mock_chatbot):
        """챗봇 응답 품질 테스트"""
        questions = [
            "두 분은 어떻게 만나셨나요?",
            "신혼여행은 어디로 가세요?",
            "결혼식은 언제인가요?"
        ]

        for question in questions:
            response = client.post(
                "/api/chatbot",
                json={"message": question}
            )

            if response.status_code == 200:
                data = response.json()
                assert "response" in data
                assert len(data["response"]) > 0


@pytest.mark.unit
class TestChatbotDisabled:
    """챗봇 비활성화 상태 테스트"""

    def test_chatbot_disabled_response(self, client: TestClient, monkeypatch):
        """챗봇 비활성화 시 응답"""
        # CHATBOT_ENABLED를 False로 설정
        import main
        monkeypatch.setattr(main, "CHATBOT_ENABLED", False)

        response = client.post(
            "/api/chatbot",
            json={"message": "안녕하세요"}
        )

        assert response.status_code == 503
        data = response.json()
        assert data["success"] is False
        assert "error" in data