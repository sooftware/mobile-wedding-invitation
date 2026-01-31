"""Chatbot Initialization and Management.

This module handles chatbot functionality:
- Checking if chatbot modules are available
- Initializing chatbot with configuration
- Managing chatbot enabled/disabled state

The chatbot uses LangChain/LangGraph for conversational AI,
with couple-specific knowledge loaded from JSON files.

If chatbot modules are not available, the system gracefully
degrades to a fallback mode without breaking the application.
"""

import logging
from pathlib import Path
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# 챗봇 모듈 import 시도
try:
    from app.chatbot import get_chatbot, initialize_chatbot
    from app.chatbot.schemas import ChatbotMessage

    CHATBOT_ENABLED = True
    logger.info("챗봇 모듈을 성공적으로 불러왔습니다.")
except ImportError as e:
    logger.warning(f"챗봇 모듈을 불러올 수 없습니다: {e}")
    logger.warning("챗봇 기능이 비활성화됩니다.")
    CHATBOT_ENABLED = False


    # 폴백 모델 정의
    class ChatbotMessage(BaseModel):
        message: str


    get_chatbot = None
    initialize_chatbot = None


def init_chatbot():
    """Initialize chatbot with configuration files.

    Loads configuration from:
    - config/config.json: General application config
    - config/couple_knowledge.json: Couple-specific Q&A knowledge base

    Falls back to legacy file locations if new paths don't exist.

    Returns:
        None

    Note:
        If chatbot is disabled or initialization fails, the application
        continues running without chatbot functionality. Errors are logged
        but don't crash the application.
    """
    if not CHATBOT_ENABLED:
        logger.info("챗봇이 비활성화되어 있습니다.")
        return

    try:
        config_path = "config/config.json" if Path("config/config.json").exists() else "config.json"
        knowledge_path = "config/couple_knowledge.json" if Path(
            "config/couple_knowledge.json").exists() else "couple_knowledge.json"
        initialize_chatbot(config_path, knowledge_path)
        logger.info("✅ 챗봇이 성공적으로 초기화되었습니다.")
    except Exception as e:
        logger.error(f"⚠️ 챗봇 초기화 실패: {e}")
        logger.warning("챗봇 없이 서버를 시작합니다.")