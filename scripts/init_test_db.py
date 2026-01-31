#!/usr/bin/env python3
"""
테스트 DB 초기화 스크립트
테스트 실행 전 DB를 깨끗하게 초기화합니다.
"""

import sqlite3
import os

# 테스트용 DB 경로
DB_PATH = "wedding.db"


def init_test_db():
    """테스트 DB 초기화"""

    # 기존 DB 삭제
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  기존 DB 삭제: {DB_PATH}")

    # 새 DB 생성
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # guestbook 테이블
    cursor.execute("""
                   CREATE TABLE guestbook
                   (
                       id            INTEGER PRIMARY KEY AUTOINCREMENT,
                       name          TEXT NOT NULL,
                       message       TEXT NOT NULL,
                       password_hash TEXT NOT NULL,
                       timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    print("✅ guestbook 테이블 생성")

    # rsvp 테이블
    cursor.execute("""
                   CREATE TABLE rsvp
                   (
                       id           INTEGER PRIMARY KEY AUTOINCREMENT,
                       which_side   TEXT NOT NULL,
                       can_attend   TEXT NOT NULL,
                       guest_name   TEXT NOT NULL,
                       phone_number TEXT,
                       timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   """)
    print("✅ rsvp 테이블 생성")

    conn.commit()
    conn.close()

    print(f"\n🎉 테스트 DB 초기화 완료: {DB_PATH}")
    print("이제 pytest를 실행하세요!")


if __name__ == "__main__":
    init_test_db()