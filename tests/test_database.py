"""
Database Tests
- 데이터베이스 쿼리 및 연결 테스트

Author: Soohwan Kim (2025.10)
"""

import pytest
from app.database import DatabaseQueries, get_query, get_create_queries


@pytest.mark.database
@pytest.mark.unit
class TestDatabaseQueries:
    """데이터베이스 쿼리 테스트"""

    def test_get_query_guestbook(self):
        """방명록 쿼리 가져오기"""
        query = get_query("guestbook", "select_all")
        assert "SELECT" in query
        assert "guestbook" in query
        assert "ORDER BY" in query

    def test_get_query_rsvp(self):
        """RSVP 쿼리 가져오기"""
        query = get_query("rsvp", "select_all")
        assert "SELECT" in query
        assert "rsvp" in query

    def test_get_query_with_db_type(self):
        """데이터베이스 타입별 쿼리"""
        # SQLite
        sqlite_query = get_query("guestbook", "insert", "sqlite")
        assert "?" in sqlite_query

        # PostgreSQL
        pg_query = get_query("guestbook", "insert", "postgresql")
        assert "%s" in pg_query

    def test_get_create_table_queries(self):
        """테이블 생성 쿼리"""
        queries = get_create_queries("sqlite")
        assert "guestbook" in queries
        assert "rsvp" in queries
        assert "CREATE TABLE" in queries["guestbook"]

    def test_get_nonexistent_query(self):
        """존재하지 않는 쿼리"""
        query = get_query("nonexistent", "nonexistent")
        assert query == ""

    def test_database_type_detection(self):
        """데이터베이스 타입 감지"""
        # URL이 있으면 PostgreSQL
        db_type = DatabaseQueries.get_db_type("postgresql://user:pass@host/db")
        assert db_type == "postgresql"

        # URL이 없으면 SQLite
        db_type = DatabaseQueries.get_db_type(None)
        assert db_type == "sqlite"

    def test_list_available_queries(self):
        """사용 가능한 쿼리 목록"""
        queries = DatabaseQueries.list_available_queries()
        assert "guestbook" in queries
        assert "rsvp" in queries
        assert "stats" in queries
        assert isinstance(queries["guestbook"], list)


@pytest.mark.database
@pytest.mark.integration
class TestDatabaseConnection:
    """데이터베이스 연결 테스트"""

    def test_db_connection_works(self, db_connection):
        """데이터베이스 연결 성공"""
        assert db_connection is not None
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result is not None

    def test_tables_exist(self, db_connection):
        """필요한 테이블들이 존재"""
        cursor = db_connection.cursor()

        # SQLite
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        assert "guestbook" in tables
        assert "rsvp" in tables

    def test_guestbook_table_structure(self, db_connection):
        """방명록 테이블 구조"""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(guestbook)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {"id", "name", "message", "password_hash", "timestamp"}
        assert required_columns.issubset(columns)

    def test_rsvp_table_structure(self, db_connection):
        """RSVP 테이블 구조"""
        cursor = db_connection.cursor()
        cursor.execute("PRAGMA table_info(rsvp)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {"id", "which_side", "can_attend", "guest_name", "phone_number", "timestamp"}
        assert required_columns.issubset(columns)


@pytest.mark.database
@pytest.mark.unit
class TestQueryExecution:
    """쿼리 실행 테스트"""

    def test_insert_guestbook(self, db_connection):
        """방명록 삽입"""
        cursor = db_connection.cursor()
        query = get_query("guestbook", "insert", "sqlite")

        cursor.execute(query, ("테스트", "메시지", "hash"))
        db_connection.commit()

        cursor.execute("SELECT COUNT(*) FROM guestbook")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_insert_rsvp(self, db_connection):
        """RSVP 삽입"""
        cursor = db_connection.cursor()
        query = get_query("rsvp", "insert", "sqlite")

        cursor.execute(query, ("신랑측", "참석할게요", "김하객", "010-1234-5678"))
        db_connection.commit()

        cursor.execute("SELECT COUNT(*) FROM rsvp")
        count = cursor.fetchone()[0]
        assert count == 1

    def test_delete_guestbook(self, db_connection):
        """방명록 삭제"""
        cursor = db_connection.cursor()

        # 삽입
        insert_query = get_query("guestbook", "insert", "sqlite")
        cursor.execute(insert_query, ("테스트", "메시지", "hash"))
        db_connection.commit()

        # ID 가져오기
        cursor.execute("SELECT id FROM guestbook LIMIT 1")
        entry_id = cursor.fetchone()[0]

        # 삭제
        delete_query = get_query("guestbook", "delete", "sqlite")
        cursor.execute(delete_query, (entry_id,))
        db_connection.commit()

        # 확인
        cursor.execute("SELECT COUNT(*) FROM guestbook")
        count = cursor.fetchone()[0]
        assert count == 0

    def test_delete_rsvp(self, db_connection):
        """RSVP 삭제"""
        cursor = db_connection.cursor()

        # 삽입
        insert_query = get_query("rsvp", "insert", "sqlite")
        cursor.execute(insert_query, ("신랑측", "참석할게요", "김하객", "010-1234-5678"))
        db_connection.commit()

        # ID 가져오기
        cursor.execute("SELECT id FROM rsvp LIMIT 1")
        entry_id = cursor.fetchone()[0]

        # 삭제
        delete_query = get_query("rsvp", "delete", "sqlite")
        cursor.execute(delete_query, (entry_id,))
        db_connection.commit()

        # 확인
        cursor.execute("SELECT COUNT(*) FROM rsvp")
        count = cursor.fetchone()[0]
        assert count == 0


@pytest.mark.database
class TestDatabaseStats:
    """데이터베이스 통계 쿼리 테스트"""

    def test_count_guestbook(self, db_connection):
        """방명록 카운트"""
        cursor = db_connection.cursor()
        query = get_query("stats", "count_guestbook")
        cursor.execute(query)
        count = cursor.fetchone()[0]
        assert count >= 0

    def test_count_rsvp(self, db_connection):
        """RSVP 카운트"""
        cursor = db_connection.cursor()
        query = get_query("stats", "count_rsvp")
        cursor.execute(query)
        count = cursor.fetchone()[0]
        assert count >= 0