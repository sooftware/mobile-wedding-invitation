"""Chatbot Router.

AI-powered chatbot for answering wedding-related questions.
Uses LangChain/LangGraph with couple-specific knowledge base.

Features:
    - Natural language processing
    - Context-aware responses
    - Couple-specific Q&A
    - Graceful degradation if chatbot unavailable

Routes:
    POST /api/chatbot: Send message to chatbot
"""

import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.config import config
from app.core.chatbot_init import CHATBOT_ENABLED, get_chatbot, ChatbotMessage

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
logger = logging.getLogger(__name__)


@router.post("")
async def chatbot_endpoint(message_data: ChatbotMessage):
    """Process chatbot message and return AI response.

    Sends user message to LangChain-powered chatbot and returns
    contextual response based on couple-specific knowledge.

    Args:
        message_data (ChatbotMessage): Contains user's message text

    Returns:
        JSONResponse: {
            "success": bool,
            "response": str (chatbot's reply),
            "error": str (optional, if error occurred)
        }

    Status Codes:
        200: Successful response
        500: Internal error (chatbot malfunction)
        503: Service unavailable (chatbot disabled)

    Note:
        If chatbot is disabled, returns friendly error message
        without breaking the application flow.
    """
    logger.info(f"챗봇 API 호출: {message_data.message}")

    if not CHATBOT_ENABLED:
        logger.warning("챗봇이 비활성화되어 있습니다.")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "response": "죄송해요 😅 챗봇 서비스가 현재 이용할 수 없어요. 잠시 후 다시 시도해주세요!",
                "error": "Chatbot service unavailable"
            }
        )

    try:
        chatbot = get_chatbot()
        if not chatbot:
            logger.error("챗봇 인스턴스를 가져올 수 없습니다.")
            raise Exception("Chatbot instance not available")

        # 비동기 응답 생성 (멀티턴 대화 지원)
        response = await chatbot.get_response(
            query=message_data.message,
            chat_history=message_data.chat_history,
            thread_id=message_data.thread_id or "default"
        )

        logger.info(f"챗봇 응답 생성 완료: {response.get('success', False)}")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"챗봇 API 에러: {str(e)}", exc_info=True)

        # config에서 에러 메시지 가져오기 (또는 기본값)
        error_message = config.get('content', {}).get('chatbot', {}).get('error_message',
                                                                         "앗! 잠시 문제가 생겼네요 😅 조금 후에 다시 시도해주세요!")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "response": error_message,
                "error": str(e)
            }
        )