"""
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License.

Database Queries
- PostgreSQL과 SQLite 모두 지원

Author: Soohwan Kim (2025.09)
Updated: 2025.10 (RSVP delete 쿼리 추가)
"""

from typing import Dict, Tuple


class DatabaseQueries:
    """데이터베이스 쿼리 관리 클래스"""

    # =============================================================================
    # 테이블 생성 쿼리들
    # =============================================================================

    CREATE_TABLES = {
        "postgresql": {
            "guestbook": """
                         CREATE TABLE IF NOT EXISTS guestbook
                         (
                             id
                             SERIAL
                             PRIMARY
                             KEY,
                             name
                             VARCHAR
                         (
                             100
                         ) NOT NULL,
                             message TEXT NOT NULL,
                             password_hash VARCHAR
                         (
                             64
                         ) NOT NULL,
                             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )
                         """,
            "rsvp": """
                    CREATE TABLE IF NOT EXISTS rsvp
                    (
                        id
                        SERIAL
                        PRIMARY
                        KEY,
                        which_side
                        VARCHAR
                    (
                        10
                    ) NOT NULL,
                        can_attend VARCHAR
                    (
                        20
                    ) NOT NULL,
                        guest_name VARCHAR
                    (
                        100
                    ) NOT NULL,
                        phone_number VARCHAR
                    (
                        20
                    ),
                        companion_count INTEGER DEFAULT 1,
                        meal_attendance VARCHAR
                    (
                        20
                    ),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """,
            "visitor_stats": """
                             CREATE TABLE IF NOT EXISTS visitor_stats
                             (
                                 id
                                 SERIAL
                                 PRIMARY
                                 KEY,
                                 visit_date
                                 DATE
                                 NOT
                                 NULL,
                                 ip_address
                                 VARCHAR
                             (
                                 45
                             ),
                                 user_agent TEXT,
                                 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                 )
                             """,
            "photos": """
                      CREATE TABLE IF NOT EXISTS photos
                      (
                          id
                          SERIAL
                          PRIMARY
                          KEY,
                          filename
                          VARCHAR
                      (
                          255
                      ) NOT NULL,
                          file_path VARCHAR
                      (
                          500
                      ) NOT NULL,
                          file_size INTEGER NOT NULL,
                          content_type VARCHAR
                      (
                          50
                      ),
                          uploader_name VARCHAR
                      (
                          100
                      ),
                          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                          )
                      """
        },
        "sqlite": {
            "guestbook": """
                         CREATE TABLE IF NOT EXISTS guestbook
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             name
                             TEXT
                             NOT
                             NULL,
                             message
                             TEXT
                             NOT
                             NULL,
                             password_hash
                             TEXT
                             NOT
                             NULL,
                             timestamp
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """,
            "rsvp": """
                    CREATE TABLE IF NOT EXISTS rsvp
                    (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        which_side
                        TEXT
                        NOT
                        NULL,
                        can_attend
                        TEXT
                        NOT
                        NULL,
                        guest_name
                        TEXT
                        NOT
                        NULL,
                        phone_number
                        TEXT,
                        companion_count
                        INTEGER
                        DEFAULT
                        1,
                        meal_attendance
                        TEXT,
                        timestamp
                        DATETIME
                        DEFAULT
                        CURRENT_TIMESTAMP
                    )
                    """,
            "visitor_stats": """
                             CREATE TABLE IF NOT EXISTS visitor_stats
                             (
                                 id
                                 INTEGER
                                 PRIMARY
                                 KEY
                                 AUTOINCREMENT,
                                 visit_date
                                 DATE
                                 NOT
                                 NULL,
                                 ip_address
                                 TEXT,
                                 user_agent
                                 TEXT,
                                 timestamp
                                 DATETIME
                                 DEFAULT
                                 CURRENT_TIMESTAMP
                                 )
                             """,
            "photos": """
                      CREATE TABLE IF NOT EXISTS photos
                      (
                          id
                          INTEGER
                          PRIMARY
                          KEY
                          AUTOINCREMENT,
                          filename
                          TEXT
                          NOT
                          NULL,
                          file_path
                          TEXT
                          NOT
                          NULL,
                          file_size
                          INTEGER
                          NOT
                          NULL,
                          content_type
                          TEXT,
                          uploader_name
                          TEXT,
                          timestamp
                          DATETIME
                          DEFAULT
                          CURRENT_TIMESTAMP
                      )
                      """
        }
    }

    # =============================================================================
    # 방명록 쿼리들
    # =============================================================================

    GUESTBOOK = {
        # 전체 조회 (최신순)
        "select_all": """
            SELECT id, name, message, timestamp
            FROM guestbook
            ORDER BY timestamp DESC
        """,

        # 전체 개수 조회
        "count_all": "SELECT COUNT(*) as count FROM guestbook",

        # 새 방명록 추가
        "insert": {
            "postgresql": "INSERT INTO guestbook (name, message, password_hash) VALUES (%s, %s, %s)",
            "sqlite": "INSERT INTO guestbook (name, message, password_hash) VALUES (?, ?, ?)"
        },

        # 비밀번호 확인용 (ID로 조회)
        "select_by_id": {
            "postgresql": "SELECT password_hash FROM guestbook WHERE id = %s",
            "sqlite": "SELECT password_hash FROM guestbook WHERE id = ?"
        },

        # 수정용 데이터 조회 (비밀번호 + 내용)
        "select_with_content": {
            "postgresql": "SELECT password_hash, name, message FROM guestbook WHERE id = %s",
            "sqlite": "SELECT password_hash, name, message FROM guestbook WHERE id = ?"
        },

        # 방명록 수정
        "update": {
            "postgresql": "UPDATE guestbook SET name = %s, message = %s WHERE id = %s",
            "sqlite": "UPDATE guestbook SET name = ?, message = ? WHERE id = ?"
        },

        # 방명록 삭제
        "delete": {
            "postgresql": "DELETE FROM guestbook WHERE id = %s",
            "sqlite": "DELETE FROM guestbook WHERE id = ?"
        }
    }

    # =============================================================================
    # RSVP 쿼리들
    # =============================================================================

    RSVP = {
        # 새 RSVP 추가 - companion_count, meal_attendance 추가
        "insert": {
            "postgresql": """
                          INSERT INTO rsvp (which_side, can_attend, guest_name, phone_number, companion_count, meal_attendance)
                          VALUES (%s, %s, %s, %s, %s, %s)
                          """,
            "sqlite": """
                      INSERT INTO rsvp (which_side, can_attend, guest_name, phone_number, companion_count, meal_attendance)
                      VALUES (?, ?, ?, ?, ?, ?)
                      """
        },

        # 전체 RSVP 조회 - companion_count, meal_attendance 추가
        "select_all": """
                      SELECT id, which_side, can_attend, guest_name, phone_number, companion_count, meal_attendance, timestamp
                      FROM rsvp
                      ORDER BY timestamp DESC
                      """,

        # 참석자만 조회 - companion_count, meal_attendance 추가
        "select_attending": """
                            SELECT id, which_side, guest_name, phone_number, companion_count, meal_attendance, timestamp
                            FROM rsvp
                            WHERE can_attend = '참석할게요'
                            ORDER BY which_side, guest_name
                            """,

        # 기존 쿼리들은 그대로 유지
        "count_by_side": """
                         SELECT which_side, can_attend, COUNT(*) as count
                         FROM rsvp
                         GROUP BY which_side, can_attend
                         ORDER BY which_side, can_attend
                         """,

        "delete": {
            "postgresql": "DELETE FROM rsvp WHERE id = %s",
            "sqlite": "DELETE FROM rsvp WHERE id = ?"
        }
    }

    # =============================================================================
    # 통계 쿼리들
    # =============================================================================

    STATS = {
        # 기본 카운트
        "count_guestbook": "SELECT COUNT(*) FROM guestbook",
        "count_rsvp": "SELECT COUNT(*) FROM rsvp",

        # 상세 통계
        "guestbook_monthly": """
            SELECT 
                DATE_TRUNC('month', timestamp) as month,
                COUNT(*) as count
            FROM guestbook 
            GROUP BY DATE_TRUNC('month', timestamp)
            ORDER BY month DESC
        """,

        "rsvp_summary": """
            SELECT 
                can_attend,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
            FROM rsvp 
            GROUP BY can_attend
            ORDER BY count DESC
        """
    }

    # =============================================================================
    # 사진 쿼리들
    # =============================================================================

    PHOTOS = {
        # 사진 추가
        "insert": {
            "postgresql": """
                          INSERT INTO photos (filename, file_path, file_size, content_type, uploader_name)
                          VALUES (%s, %s, %s, %s, %s)
                          RETURNING id
                          """,
            "sqlite": """
                      INSERT INTO photos (filename, file_path, file_size, content_type, uploader_name)
                      VALUES (?, ?, ?, ?, ?)
                      """
        },

        # 전체 사진 조회 (최신순)
        "select_all": """
                      SELECT id, filename, file_path, file_size, content_type, uploader_name, timestamp
                      FROM photos
                      ORDER BY timestamp DESC
                      """,

        # 사진 개수 조회
        "count_all": "SELECT COUNT(*) as count FROM photos",

        # 사진 삭제
        "delete": {
            "postgresql": "DELETE FROM photos WHERE id = %s RETURNING file_path",
            "sqlite": "DELETE FROM photos WHERE id = ?"
        },

        # ID로 사진 조회
        "select_by_id": {
            "postgresql": "SELECT * FROM photos WHERE id = %s",
            "sqlite": "SELECT * FROM photos WHERE id = ?"
        }
    }

    # =============================================================================
    # 방문자 통계 쿼리들
    # =============================================================================

    VISITOR_STATS = {
        # 방문 기록 추가 (매번 카운트)
        "insert": {
            "postgresql": """
                          INSERT INTO visitor_stats (visit_date, ip_address, user_agent)
                          VALUES (%s, %s, %s)
                          """,
            "sqlite": """
                      INSERT INTO visitor_stats (visit_date, ip_address, user_agent)
                      VALUES (?, ?, ?)
                      """
        },

        # 오늘 방문자 수 (모든 방문 카운트)
        "count_today": {
            "postgresql": """
                          SELECT COUNT(*) as count
                          FROM visitor_stats
                          WHERE visit_date = CURRENT_DATE
                          """,
            "sqlite": """
                      SELECT COUNT(*) as count
                      FROM visitor_stats
                      WHERE visit_date = DATE ('now')
                      """
        },

        # 총 방문자 수 (모든 방문 카운트)
        "count_total": """
                       SELECT COUNT(*) as total_count
                       FROM visitor_stats
                       """,

        # 일별 방문자 통계 (최근 30일)
        "daily_stats": """
                       SELECT visit_date,
                              COUNT(DISTINCT ip_address) as unique_visitors,
                              COUNT(*)                   as total_visits
                       FROM visitor_stats
                       GROUP BY visit_date
                       ORDER BY visit_date DESC LIMIT 30
                       """
    }

    # =============================================================================
    # 유틸리티 메서드들
    # =============================================================================

    @classmethod
    def get_query(cls, category: str, query_name: str, db_type: str = "sqlite") -> str:
        """
        쿼리 가져오기

        Args:
            category: 쿼리 카테고리 (guestbook, rsvp, stats)
            query_name: 쿼리 이름
            db_type: 데이터베이스 타입 (postgresql, sqlite)

        Returns:
            SQL 쿼리 문자열

        Example:
            >>> DatabaseQueries.get_query("guestbook", "select_all")
            'SELECT id, name, message, timestamp FROM guestbook ORDER BY timestamp DESC'
        """
        category_queries = getattr(cls, category.upper(), {})
        query = category_queries.get(query_name)

        if isinstance(query, dict):
            return query.get(db_type, query.get("sqlite", ""))
        return query or ""

    @classmethod
    def get_create_table_queries(cls, db_type: str = "sqlite") -> Dict[str, str]:
        """
        테이블 생성 쿼리들 가져오기

        Args:
            db_type: 데이터베이스 타입

        Returns:
            테이블명: 쿼리 딕셔너리
        """
        return cls.CREATE_TABLES.get(db_type, cls.CREATE_TABLES["sqlite"])

    @classmethod
    def get_db_type(cls, database_url: str = None) -> str:
        """
        데이터베이스 타입 판별

        Args:
            database_url: 데이터베이스 URL (없으면 SQLite)

        Returns:
            "postgresql" 또는 "sqlite"
        """
        return "postgresql" if database_url else "sqlite"

    @classmethod
    def list_available_queries(cls) -> Dict[str, list]:
        """
        사용 가능한 모든 쿼리 목록 반환

        Returns:
            카테고리별 쿼리 이름 목록
        """
        return {
            "guestbook": list(cls.GUESTBOOK.keys()),
            "rsvp": list(cls.RSVP.keys()),
            "stats": list(cls.STATS.keys()),
            "visitor_stats": list(cls.VISITOR_STATS.keys()),
            "photos": list(cls.PHOTOS.keys())
        }


# =============================================================================
# 편의 함수들 (Shorthand functions)
# =============================================================================

def get_query(category: str, query_name: str, db_type: str = "sqlite") -> str:
    """쿼리 가져오기 편의 함수"""
    return DatabaseQueries.get_query(category, query_name, db_type)


def get_create_queries(db_type: str = "sqlite") -> Dict[str, str]:
    """테이블 생성 쿼리 가져오기 편의 함수"""
    return DatabaseQueries.get_create_table_queries(db_type)


def list_queries() -> Dict[str, list]:
    """사용 가능한 쿼리 목록 보기 편의 함수"""
    return DatabaseQueries.list_available_queries()


# =============================================================================
# 개발용 디버깅 함수들
# =============================================================================

if __name__ == "__main__":
    print("📋 사용 가능한 쿼리들:")
    for category, queries in list_queries().items():
        print(f"\n🔹 {category.upper()}")
        for query_name in queries:
            print(f"  - {query_name}")

    print(f"\n✅ 총 {sum(len(q) for q in list_queries().values())}개 쿼리 등록됨")
