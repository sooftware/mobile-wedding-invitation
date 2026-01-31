"""
Mobile Wedding Invitation App with Admin Panel
- A simple web application for a wedding invitation.
- Features guestbook, RSVP, AI chatbot, and admin panel functionalities.
- Uses FastAPI for backend and Jinja2 for templating.
- Supports both local SQLite and PostgreSQL (Railway) databases.
- Clean modular structure with app/ backend organization.
- Developed by Soohwan Kim & Claude-4
"""

import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

# 코어 모듈
from app.core import config, init_db, migrate_database, init_chatbot, SECRET_KEY, APP_TITLE, DATABASE_URL

# 라우터
from app.routers import home, guestbook, rsvp, admin, chatbot, stats, photos

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title=APP_TITLE)

# 미들웨어
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# 정적 파일
app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(home.router)
app.include_router(guestbook.router)
app.include_router(rsvp.router)
app.include_router(admin.router)
app.include_router(chatbot.router)
app.include_router(stats.router)
app.include_router(photos.router)


@app.on_event("startup")
async def startup_event():
    """앱 시작시 초기화"""
    logger.info("애플리케이션 시작 중...")

    # 환경변수 확인
    if DATABASE_URL:
        logger.info("✅ PostgreSQL 데이터베이스 사용 (프로덕션)")
    else:
        logger.info("⚠️ SQLite 데이터베이스 사용 (개발환경)")

    # 데이터베이스 초기화
    try:
        init_db()
        logger.info("✅ 데이터베이스 초기화 완료")

        # 마이그레이션 실행
        migrate_database()

    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
        raise e

    # 챗봇 초기화
    init_chatbot()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)