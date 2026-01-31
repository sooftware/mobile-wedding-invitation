"""
Database Migration: Remove UNIQUE constraint from visitor_stats table

This migration removes the UNIQUE(visit_date, ip_address) constraint
to allow counting every visit instead of unique daily visitors.

Usage:
    python scripts/migrate_visitor_stats.py

Author: Soohwan Kim
Date: 2025-01
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def migrate_sqlite():
    """Migrate SQLite database - recreate table without UNIQUE constraint"""
    print("🔄 SQLite 마이그레이션 시작...")

    conn = sqlite3.connect('wedding.db')
    cursor = conn.cursor()

    try:
        # 1. 기존 데이터 백업
        cursor.execute("SELECT COUNT(*) FROM visitor_stats")
        count = cursor.fetchone()[0]
        print(f"📊 기존 레코드 수: {count}")

        # 2. 임시 테이블 생성 (UNIQUE 제약 없음)
        cursor.execute("""
            CREATE TABLE visitor_stats_new
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visit_date DATE NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 새 테이블 생성 완료")

        # 3. 데이터 복사
        cursor.execute("""
            INSERT INTO visitor_stats_new (id, visit_date, ip_address, user_agent, timestamp)
            SELECT id, visit_date, ip_address, user_agent, timestamp
            FROM visitor_stats
        """)
        print("✅ 데이터 복사 완료")

        # 4. 기존 테이블 삭제
        cursor.execute("DROP TABLE visitor_stats")
        print("✅ 기존 테이블 삭제 완료")

        # 5. 새 테이블 이름 변경
        cursor.execute("ALTER TABLE visitor_stats_new RENAME TO visitor_stats")
        print("✅ 테이블 이름 변경 완료")

        # 6. 확인
        cursor.execute("SELECT COUNT(*) FROM visitor_stats")
        new_count = cursor.fetchone()[0]
        print(f"📊 마이그레이션 후 레코드 수: {new_count}")

        if count == new_count:
            print("✅ 데이터 무결성 확인 완료!")
        else:
            print(f"⚠️ 경고: 레코드 수가 다릅니다! (이전: {count}, 이후: {new_count})")

        conn.commit()
        print("✅ SQLite 마이그레이션 완료!")

    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_postgresql():
    """Migrate PostgreSQL database - drop UNIQUE constraint"""
    print("🔄 PostgreSQL 마이그레이션 시작...")

    import psycopg2
    from urllib.parse import urlparse

    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cursor = conn.cursor()

    try:
        # 1. 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM visitor_stats")
        count = cursor.fetchone()[0]
        print(f"📊 기존 레코드 수: {count}")

        # 2. UNIQUE 제약조건 이름 찾기
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'visitor_stats'
            AND constraint_type = 'UNIQUE'
        """)

        constraints = cursor.fetchall()

        if constraints:
            for (constraint_name,) in constraints:
                print(f"🔍 발견된 UNIQUE 제약: {constraint_name}")
                cursor.execute(f"ALTER TABLE visitor_stats DROP CONSTRAINT {constraint_name}")
                print(f"✅ 제약조건 {constraint_name} 제거 완료")
        else:
            print("ℹ️ UNIQUE 제약조건이 없습니다 (이미 제거되었거나 존재하지 않음)")

        conn.commit()
        print("✅ PostgreSQL 마이그레이션 완료!")

    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("방문자 통계 테이블 마이그레이션")
    print("UNIQUE 제약조건 제거 - 모든 방문 카운트 가능")
    print("=" * 60)
    print()

    if DATABASE_URL:
        print(f"📍 Database: PostgreSQL ({DATABASE_URL[:30]}...)")
        migrate_postgresql()
    else:
        print("📍 Database: SQLite (wedding.db)")
        migrate_sqlite()

    print()
    print("=" * 60)
    print("🎉 마이그레이션 성공!")
    print("이제 모든 방문이 카운트됩니다 (같은 IP도 매번 카운트)")
    print("=" * 60)
