"""
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License.

Admin Module
- 관리자 페이지 및 인증 관련 기능

Author: Soohwan Kim (2025.10)
"""

from .auth import get_current_admin, verify_admin_credentials

__all__ = [
    "get_current_admin",
    "verify_admin_credentials",
]