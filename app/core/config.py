"""Core Configuration Module.

This module handles application configuration management, including:
- Loading configuration from JSON files
- Managing environment variables
- Defining global constants

The configuration is loaded from config/config.json and includes
wedding-specific information, content settings, and application metadata.

Environment Variables:
    SECRET_KEY: Secret key for session middleware (auto-generated if not set)
    KAKAO_APP_KEY: Kakao API key for map integration
    DATABASE_URL: PostgreSQL connection URL (uses SQLite if not set)
"""

import os
import json
import secrets
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def load_config():
    """Load application configuration from JSON file.

    Attempts to load config.json from the following locations in order:
    1. config/config.json (preferred location)
    2. config.json (legacy location for backwards compatibility)

    Returns:
        dict: Configuration dictionary containing wedding info, content, etc.

    Raises:
        Exception: If config.json is not found
        Exception: If config.json contains invalid JSON
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    if not config_path.exists():
        # 기존 위치에서 찾기 (하위호환)
        config_path = Path(__file__).parent.parent.parent / "config.json"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception("config.json 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        raise Exception("config.json 파일 형식이 올바르지 않습니다.")


# 설정 로드
config = load_config()

# 환경변수
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
KAKAO_APP_KEY = os.getenv("KAKAO_APP_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL")

# 앱 타이틀
APP_TITLE = f"{config['wedding']['groom']['name_kr']} ♥ {config['wedding']['bride']['name_kr']} 결혼식 청첩장"