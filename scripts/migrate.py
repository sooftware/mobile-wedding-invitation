import sqlite3
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "..."

if DATABASE_URL:
    # PostgreSQL
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
    print("PostgreSQL 연결됨")
else:
    # SQLite
    conn = sqlite3.connect('wedding.db')
    print("SQLite 연결됨")

cursor = conn.cursor()

# 1. RSVP 테이블에 컬럼 추가
try:
    if DATABASE_URL:
        cursor.execute("ALTER TABLE rsvp ADD COLUMN IF NOT EXISTS companion_count INTEGER DEFAULT 1")
    else:
        cursor.execute("ALTER TABLE rsvp ADD COLUMN companion_count INTEGER DEFAULT 1")
    print("✅ companion_count 컬럼 추가 완료")
except Exception as e:
    print(f"⚠️ companion_count 컬럼 이미 존재: {e}")

# 1-2. RSVP 테이블에 meal_attendance 컬럼 추가
try:
    if DATABASE_URL:
        cursor.execute("ALTER TABLE rsvp ADD COLUMN IF NOT EXISTS meal_attendance VARCHAR(20)")
    else:
        cursor.execute("ALTER TABLE rsvp ADD COLUMN meal_attendance TEXT")
    print("✅ meal_attendance 컬럼 추가 완료")
except Exception as e:
    print(f"⚠️ meal_attendance 컬럼 이미 존재: {e}")

# 2. visitor_stats 테이블 생성
try:
    if DATABASE_URL:
        cursor.execute("""
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
                           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           UNIQUE
                       (
                           visit_date,
                           ip_address
                       )
                           )
                       """)
    else:
        cursor.execute("""
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
                           CURRENT_TIMESTAMP,
                           UNIQUE
                       (
                           visit_date,
                           ip_address
                       )
                           )
                       """)
    print("✅ visitor_stats 테이블 생성 완료")
except Exception as e:
    print(f"⚠️ 테이블 생성 실패: {e}")

conn.commit()
conn.close()
print("✅ 마이그레이션 완료!")