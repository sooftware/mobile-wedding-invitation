#!/usr/bin/env python3
"""
관리자 비밀번호 해시 생성 도구

사용법:
    python generate_password_hash.py

Author: Soohwan Kim (2025.10)
"""

import hashlib
import getpass


def generate_password_hash():
    """비밀번호 해시 생성"""
    print("=" * 60)
    print("🔐 관리자 비밀번호 해시 생성 도구")
    print("=" * 60)
    print()

    # 비밀번호 입력
    while True:
        password = getpass.getpass("새 비밀번호를 입력하세요: ")

        if len(password) < 8:
            print("❌ 비밀번호는 최소 8자 이상이어야 합니다.")
            continue

        password_confirm = getpass.getpass("비밀번호를 다시 입력하세요: ")

        if password != password_confirm:
            print("❌ 비밀번호가 일치하지 않습니다. 다시 시도하세요.")
            continue

        break

    # 해시 생성
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    print()
    print("=" * 60)
    print("✅ 비밀번호 해시가 생성되었습니다!")
    print("=" * 60)
    print()
    print("📋 .env 파일에 다음 내용을 추가하세요:")
    print()
    print("-" * 60)
    print(f"ADMIN_USERNAME=${{ADMIN_USERNAME}}")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("-" * 60)
    print()
    print("⚠️  주의사항:")
    print("  • 이 해시값을 .env 파일에 저장하세요")
    print("  • .env 파일을 절대 공개하지 마세요")
    print("  • GitHub에 업로드하지 마세요")
    print()
    print("💡 팁:")
    print("  • 사용자명을 변경하려면 ADMIN_USERNAME을 수정하세요")
    print("  • 비밀번호 변경 시 이 스크립트를 다시 실행하세요")
    print()


if __name__ == "__main__":
    try:
        generate_password_hash()
    except KeyboardInterrupt:
        print("\n\n❌ 작업이 취소되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")