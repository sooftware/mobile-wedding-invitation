"""Guestbook Router.

Manages guestbook functionality for wedding guests to leave messages.
Provides full CRUD operations with password protection.

Features:
    - View all guestbook entries
    - Create new entries with password protection
    - Update entries (requires password verification)
    - Delete entries (requires password verification)
    - Password verification endpoint

Routes:
    GET /api/guestbook: List all entries
    POST /api/guestbook: Create new entry
    PUT /api/guestbook/{id}: Update existing entry
    DELETE /api/guestbook/{id}: Delete entry
    POST /api/guestbook/{id}/verify: Verify password
"""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.core.database import get_db_connection, DB_TYPE, DATABASE_URL
from app.core.utils import hash_password
from app.database.queries import get_query
from app.models import GuestbookEntry, GuestbookUpdate, DeleteGuestbookEntry, PasswordVerify

router = APIRouter(prefix="/api/guestbook", tags=["guestbook"])
logger = logging.getLogger(__name__)


@router.get("")
async def get_guestbook_entries(page: int = 1, limit: int = 10):
    """Retrieve guestbook entries with pagination.

    Returns guest messages ordered by timestamp (newest first).
    Passwords are excluded from the response for security.

    Args:
        page: Page number (1-indexed)
        limit: Number of entries per page (default: 10)

    Returns:
        dict: {
            "entries": list of entry dicts with id, name, message, timestamp
            "total": total number of entries
            "page": current page number
            "total_pages": total number of pages
        }

    Note:
        Handles both PostgreSQL (dict-based) and SQLite (tuple-based) results
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total count first
    cursor.execute(get_query("guestbook", "count_all"))
    total_count = cursor.fetchone()[0] if not DATABASE_URL else cursor.fetchone()['count']

    # Calculate pagination
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    offset = (page - 1) * limit

    # Get paginated entries
    if DATABASE_URL:
        # PostgreSQL
        cursor.execute(get_query("guestbook", "select_all") + f" LIMIT {limit} OFFSET {offset}")
    else:
        # SQLite
        cursor.execute(get_query("guestbook", "select_all") + f" LIMIT {limit} OFFSET {offset}")

    entries = []
    rows = cursor.fetchall()

    logger.info(f"📋 방명록 조회: 페이지 {page}/{total_pages}, {len(rows)}개 항목 발견")

    for row in rows:
        try:
            # PostgreSQL (RealDictCursor)과 SQLite 처리 통일
            if DATABASE_URL:
                # PostgreSQL - 딕셔너리 형태
                entry = {
                    "id": row['id'],
                    "name": row['name'],
                    "message": row['message'],
                    "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(
                        row['timestamp'])
                }
            else:
                # SQLite - 튜플 형태
                entry = {
                    "id": row[0],
                    "name": row[1],
                    "message": row[2],
                    "timestamp": row[3].isoformat() if hasattr(row[3], 'isoformat') else str(row[3])
                }
            entries.append(entry)
            logger.info(f"✅ 항목 추가: ID={entry['id']}, 이름={entry['name']}")

        except Exception as e:
            logger.error(f"❌ 방명록 항목 처리 실패: {e}, row: {row}")
            continue

    conn.close()
    logger.info(f"🎯 최종 반환: {len(entries)}개 항목 (페이지 {page}/{total_pages})")
    return {
        "entries": entries,
        "total": total_count,
        "page": page,
        "total_pages": total_pages
    }


@router.post("")
async def add_guestbook_entry(entry: GuestbookEntry):
    """Create a new guestbook entry.

    Stores guest message with hashed password for future edits/deletions.

    Args:
        entry (GuestbookEntry): Entry data with name, message, and password

    Returns:
        dict: {"status": "success", "message": "방명록이 등록되었습니다."}

    Note:
        Password is hashed using SHA-256 before storage
    """
    password_hash = hash_password(entry.password)
    conn = get_db_connection()
    cursor = conn.cursor()

    query = get_query("guestbook", "insert", DB_TYPE)
    cursor.execute(query, (entry.name, entry.message, password_hash))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "방명록이 등록되었습니다."}


@router.put("/{entry_id}")
async def update_guestbook_entry(entry_id: int, update_data: GuestbookUpdate):
    """Update an existing guestbook entry.

    Requires password verification before allowing updates.

    Args:
        entry_id (int): ID of the entry to update
        update_data (GuestbookUpdate): New data including password for verification

    Returns:
        dict: {"status": "success", "message": "메시지가 수정되었습니다."}

    Raises:
        HTTPException 400: If entry_id doesn't match update_data.id
        HTTPException 404: If entry not found
        HTTPException 403: If password is incorrect
    """
    if update_data.id != entry_id:
        raise HTTPException(status_code=400, detail="ID가 일치하지 않습니다.")

    password_hash = hash_password(update_data.password)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 비밀번호 확인
    verify_query = get_query("guestbook", "select_by_id", DB_TYPE)
    cursor.execute(verify_query, (entry_id,))

    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 메시지를 찾을 수 없습니다.")

    if result[0] != password_hash:
        conn.close()
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    # 수정
    update_query = get_query("guestbook", "update", DB_TYPE)
    cursor.execute(update_query, (update_data.name, update_data.message, entry_id))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "메시지가 수정되었습니다."}


@router.post("/{entry_id}/verify")
async def verify_password(entry_id: int, verify_data: PasswordVerify):
    """Verify password and return entry data.

    Used before edit/delete operations to confirm user owns the entry.

    Args:
        entry_id (int): ID of the entry
        verify_data (PasswordVerify): Password to verify

    Returns:
        dict: {
            "status": "success",
            "message": "비밀번호가 확인되었습니다.",
            "data": {"name": str, "message": str}
        }

    Raises:
        HTTPException 400: If entry_id doesn't match verify_data.id
        HTTPException 404: If entry not found
        HTTPException 403: If password is incorrect
    """
    if verify_data.id != entry_id:
        raise HTTPException(status_code=400, detail="ID가 일치하지 않습니다.")

    password_hash = hash_password(verify_data.password)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 비밀번호 확인 및 데이터 가져오기
    query = get_query("guestbook", "select_with_content", DB_TYPE)
    cursor.execute(query, (entry_id,))

    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 메시지를 찾을 수 없습니다.")

    if result[0] != password_hash:
        conn.close()
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    conn.close()
    return {
        "status": "success",
        "message": "비밀번호가 확인되었습니다.",
        "data": {
            "name": result[1],
            "message": result[2]
        }
    }


@router.delete("/{entry_id}")
async def delete_guestbook_entry(entry_id: int, delete_data: DeleteGuestbookEntry):
    """Delete a guestbook entry.

    Requires password verification before deletion. This operation is permanent.

    Args:
        entry_id (int): ID of the entry to delete
        delete_data (DeleteGuestbookEntry): Contains entry ID and password

    Returns:
        dict: {"status": "success", "message": "메시지가 삭제되었습니다."}

    Raises:
        HTTPException 400: If entry_id doesn't match delete_data.id
        HTTPException 404: If entry not found
        HTTPException 403: If password is incorrect
    """
    if delete_data.id != entry_id:
        raise HTTPException(status_code=400, detail="ID가 일치하지 않습니다.")

    password_hash = hash_password(delete_data.password)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 비밀번호 확인
    verify_query = get_query("guestbook", "select_by_id", DB_TYPE)
    cursor.execute(verify_query, (entry_id,))

    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 메시지를 찾을 수 없습니다.")

    if result[0] != password_hash:
        conn.close()
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    # 삭제
    delete_query = get_query("guestbook", "delete", DB_TYPE)
    cursor.execute(delete_query, (entry_id,))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "메시지가 삭제되었습니다."}