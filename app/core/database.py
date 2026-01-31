"""Database Connection and Management.

This module provides database connectivity and management functions:
- Connection pooling for PostgreSQL (production)
- SQLite fallback for development
- Database initialization and table creation
- Schema migrations

Database Types:
    - PostgreSQL: Production environment (via DATABASE_URL env var)
    - SQLite: Development environment (wedding.db file)

Connection Features:
    - Automatic reconnection with keepalives
    - Connection timeout handling
    - RealDictCursor for PostgreSQL (dict-based results)
"""

import logging
from urllib.parse import urlparse
from app.core.config import DATABASE_URL
from app.database.queries import DatabaseQueries, get_query, get_create_queries

logger = logging.getLogger(__name__)

# 데이터베이스 타입 결정
DB_TYPE = DatabaseQueries.get_db_type(DATABASE_URL)


def get_db_connection():
    """Establish and return a database connection.

    Attempts to connect to PostgreSQL if DATABASE_URL is set,
    otherwise falls back to SQLite. Includes connection pooling
    and keepalive settings for PostgreSQL.

    PostgreSQL Configuration:
        - RealDictCursor for dict-based results
        - 10s connection timeout
        - Keepalive settings to maintain connection

    SQLite Configuration:
        - Row factory for dict-like access
        - Local wedding.db file

    Returns:
        connection: Database connection object (psycopg2 or sqlite3)

    Note:
        Automatically falls back to SQLite if PostgreSQL connection fails
    """
    if DATABASE_URL:
        # PostgreSQL (Railway/Production)
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            url = urlparse(DATABASE_URL)

            connection = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                cursor_factory=RealDictCursor,
                connect_timeout=10,
                application_name='wedding_invitation',
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )

            logger.info("PostgreSQL 데이터베이스에 성공적으로 연결되었습니다.")
            return connection

        except Exception as e:
            logger.error(f"PostgreSQL 연결 실패: {e}")
            logger.info("SQLite로 폴백합니다.")
            import sqlite3
            conn = sqlite3.connect('wedding.db')
            conn.row_factory = sqlite3.Row
            return conn
    else:
        logger.info("SQLite 데이터베이스를 사용합니다.")
        import sqlite3
        conn = sqlite3.connect('wedding.db')
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Initialize database tables and verify existing data.

    Creates all required tables if they don't exist:
    - guestbook: Guest messages with password protection
    - rsvp: RSVP responses with attendance info
    - visitor_stats: Daily visitor tracking

    Also performs data validation by counting existing entries
    in guestbook and rsvp tables.

    Raises:
        Exception: If database initialization fails

    Note:
        Uses CREATE TABLE IF NOT EXISTS, safe to run multiple times
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 테이블 생성 쿼리 가져오기
        create_queries = get_create_queries(DB_TYPE)

        for table_name, query in create_queries.items():
            cursor.execute(query)
            logger.info(f"✅ {table_name} 테이블 확인/생성 완료")

        conn.commit()

        # 기존 데이터 확인
        cursor.execute(get_query("stats", "count_guestbook"))
        guestbook_result = cursor.fetchone()

        cursor.execute(get_query("stats", "count_rsvp"))
        rsvp_result = cursor.fetchone()

        # 결과 처리
        try:
            if hasattr(guestbook_result, 'keys'):
                guestbook_count = list(guestbook_result.values())[0] if guestbook_result else 0
                rsvp_count = list(rsvp_result.values())[0] if rsvp_result else 0
            else:
                guestbook_count = guestbook_result[0] if guestbook_result else 0
                rsvp_count = rsvp_result[0] if rsvp_result else 0
        except (TypeError, IndexError, AttributeError) as e:
            logger.warning(f"카운트 조회 중 에러 (무시): {e}")
            guestbook_count = 0
            rsvp_count = 0

        logger.info(f"기존 방명록 메시지: {guestbook_count}개")
        logger.info(f"기존 RSVP 응답: {rsvp_count}개")

        conn.close()
        logger.info("데이터베이스 초기화 완료")

    except Exception as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
        raise e


def migrate_database():
    """Run database schema migrations.

    Performs the following migrations:
    1. Adds companion_count column to rsvp table (if not exists)
    2. Creates visitor_stats table (if not exists)

    Migrations are idempotent and safe to run multiple times.
    Uses IF NOT EXISTS (PostgreSQL) or try-except (SQLite).

    Note:
        Errors are logged but don't stop execution, as columns/tables
        may already exist from previous migrations.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # RSVP companion_count 추가
        try:
            if DB_TYPE == "postgresql":
                cursor.execute("ALTER TABLE rsvp ADD COLUMN IF NOT EXISTS companion_count INTEGER DEFAULT 1")
            else:
                # SQLite는 IF NOT EXISTS를 지원하지 않으므로 try-except 사용
                cursor.execute("ALTER TABLE rsvp ADD COLUMN companion_count INTEGER DEFAULT 1")
            logger.info("✅ RSVP 테이블 마이그레이션 완료")
        except Exception as e:
            # 컬럼이 이미 존재하면 무시
            logger.info(f"RSVP 컬럼 이미 존재: {e}")

        # visitor_stats 테이블 생성
        try:
            create_queries = get_create_queries(DB_TYPE)
            if 'visitor_stats' in create_queries:
                cursor.execute(create_queries['visitor_stats'])
                logger.info("✅ visitor_stats 테이블 생성 완료")
        except Exception as e:
            logger.info(f"visitor_stats 테이블 이미 존재: {e}")

        conn.commit()
        conn.close()
        logger.info("✅ 데이터베이스 마이그레이션 완료")
    except Exception as e:
        logger.error(f"마이그레이션 실패: {e}")