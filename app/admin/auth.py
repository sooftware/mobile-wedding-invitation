"""
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License.

Admin Authentication
- 세션 기반 관리자 인증

Author: Soohwan Kim (2025.10)
"""

import os
import hashlib
from typing import Optional
from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


def hash_password(password: str) -> str:
    """비밀번호 해시 생성"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    관리자 인증 확인

    Args:
        username: 입력된 사용자명
        password: 입력된 비밀번호

    Returns:
        인증 성공 여부
    """
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")

    input_password_hash = hash_password(password)

    return (username == admin_username and
            input_password_hash == admin_password_hash)


def get_current_admin(request: Request) -> Optional[str]:
    """
    현재 세션의 관리자 확인

    Args:
        request: FastAPI Request 객체

    Returns:
        관리자 사용자명 또는 None

    Raises:
        HTTPException: 인증되지 않은 경우
    """
    admin_user = request.session.get("admin_user")

    if not admin_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )

    return admin_user


def require_admin(request: Request) -> str:
    """
    관리자 권한 필수 데코레이터용 함수

    Args:
        request: FastAPI Request 객체

    Returns:
        관리자 사용자명

    Raises:
        HTTPException: 인증되지 않은 경우
    """
    return get_current_admin(request)
