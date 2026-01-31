"""Core Module.

Central module providing core functionality and utilities:
- Configuration management (config.py)
- Database connections and operations (database.py)
- Common utility functions (utils.py)
- Chatbot initialization (chatbot_init.py)

This module exports commonly used functions and constants
for easy import throughout the application.
"""

from app.core.config import config, SECRET_KEY, KAKAO_APP_KEY, DATABASE_URL, APP_TITLE
from app.core.database import get_db_connection, init_db, migrate_database, DB_TYPE
from app.core.utils import hash_password, get_client_ip
from app.core.chatbot_init import init_chatbot, CHATBOT_ENABLED

__all__ = [
    'config',
    'SECRET_KEY',
    'KAKAO_APP_KEY',
    'DATABASE_URL',
    'APP_TITLE',
    'get_db_connection',
    'init_db',
    'migrate_database',
    'DB_TYPE',
    'hash_password',
    'get_client_ip',
    'init_chatbot',
    'CHATBOT_ENABLED'
]