"""
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License.

ChatBot 데이터 모델들
- 챗봇 관련 데이터클래스와 타입 정의
- Pydantic 모델들도 포함

Author: Soohwan Kim (2025.09)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from pydantic import BaseModel


@dataclass
class ChatbotConfig:
    """챗봇 설정"""
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    temperature: float = 0.7
    max_tokens: int = 300


@dataclass
class KnowledgeItem:
    """지식 베이스 아이템"""
    id: str
    topic: str
    content: str


@dataclass
class ChatResponse:
    """챗봇 응답 데이터"""
    success: bool
    response: str
    keywords: Optional[List[str]] = None
    matched_topics: Optional[List[str]] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


# Pydantic 모델들 (API용)
class ChatbotMessage(BaseModel):
    """챗봇 메시지 입력 모델"""
    message: str
    chat_history: Optional[List[Dict[str, str]]] = None  # 대화 히스토리
    thread_id: Optional[str] = None  # 대화 세션 ID


class ChatbotResponse(BaseModel):
    """챗봇 응답 모델"""
    success: bool
    response: str
    keywords: Optional[List[str]] = None
    matched_topics: Optional[List[str]] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    retry_count: Optional[int] = None
    search_queries: Optional[List[str]] = None  # 생성된 검색 쿼리들 (multi-query)
