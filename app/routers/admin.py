"""Admin Router.

Administrative panel for managing wedding invitation data.
Provides authentication and CRUD operations for guestbook and RSVP entries.

Features:
    - Admin authentication (login/logout)
    - Dashboard with statistics
    - Guestbook management (view, delete)
    - RSVP management (view, delete)
    - Visitor statistics

Routes:
    GET /admin/login: Login page
    POST /admin/login: Process login
    POST /admin/logout: Logout
    GET /admin: Dashboard (requires auth)
    GET /admin/api/rsvp: Get all RSVP entries (requires auth)
    DELETE /admin/api/rsvp/{id}: Delete RSVP entry (requires auth)
    DELETE /admin/api/guestbook/{id}: Delete guestbook entry (requires auth)
"""

import logging
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.config import config
from app.core.database import get_db_connection, DB_TYPE, DATABASE_URL
from app.database.queries import get_query, DatabaseQueries
from app.admin.auth import verify_admin_credentials, get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Render admin login page.

    Args:
        request (Request): FastAPI request object

    Returns:
        HTMLResponse: Rendered admin_login.html template
    """
    return templates.TemplateResponse("admin_login.html", {
        "request": request
    })


@router.post("/login")
async def admin_login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    """Process admin login.

    Verifies credentials and creates session on success.

    Args:
        request (Request): FastAPI request object
        username (str): Admin username from form
        password (str): Admin password from form

    Returns:
        RedirectResponse: Redirects to /admin dashboard on success

    Raises:
        HTTPException 401: If credentials are invalid
    """
    if verify_admin_credentials(username, password):
        request.session["admin_user"] = username
        return RedirectResponse(url="/admin", status_code=303)
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")


@router.post("/logout")
async def admin_logout(request: Request):
    """Process admin logout.

    Clears session data.

    Args:
        request (Request): FastAPI request object

    Returns:
        dict: {"status": "success"}
    """
    request.session.clear()
    return {"status": "success"}


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin_user: str = Depends(get_current_admin)):
    """Render admin dashboard.

    Requires authentication via get_current_admin dependency.

    Args:
        request (Request): FastAPI request object
        admin_user (str): Authenticated admin username

    Returns:
        HTMLResponse: Rendered admin.html template with config and user info
    """
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "config": config,
        "admin_user": admin_user
    })


@router.get("/api/rsvp")
async def get_admin_rsvp(request: Request, admin_user: str = Depends(get_current_admin)):
    """Retrieve all RSVP entries for admin view.

    Returns complete RSVP data including contact information.
    Requires authentication.

    Args:
        request (Request): FastAPI request object
        admin_user (str): Authenticated admin username

    Returns:
        dict: {
            "entries": list of RSVP entry dicts,
            "total": total count
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(get_query("rsvp", "select_all"))

    entries = []
    rows = cursor.fetchall()

    for row in rows:
        try:
            if DATABASE_URL:
                # PostgreSQL
                entry = {
                    "id": row['id'],
                    "which_side": row['which_side'],
                    "can_attend": row['can_attend'],
                    "guest_name": row['guest_name'],
                    "phone_number": row['phone_number'],
                    "companion_count": row.get('companion_count', 1),
                    "timestamp": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(
                        row['timestamp'])
                }
            else:
                # SQLite
                entry = {
                    "id": row[0],
                    "which_side": row[1],
                    "can_attend": row[2],
                    "guest_name": row[3],
                    "phone_number": row[4],
                    "companion_count": row[5] if len(row) > 5 else 1,
                    "timestamp": row[6] if len(row) > 6 else ""
                }
                if entry["timestamp"]:
                    entry["timestamp"] = entry["timestamp"].isoformat() if hasattr(entry["timestamp"],
                                                                                   'isoformat') else str(
                        entry["timestamp"])
            entries.append(entry)
        except Exception as e:
            logger.error(f"RSVP 항목 처리 실패: {e}")
            continue

    conn.close()
    return {"entries": entries, "total": len(entries)}


@router.delete("/api/rsvp/{entry_id}")
async def delete_admin_rsvp(
        entry_id: int,
        request: Request,
        admin_user: str = Depends(get_current_admin)
):
    """Delete RSVP entry (admin only).

    Permanently removes an RSVP entry. No password required for admin.

    Args:
        entry_id (int): ID of the RSVP entry to delete
        request (Request): FastAPI request object
        admin_user (str): Authenticated admin username

    Returns:
        dict: {"status": "success", "message": "RSVP가 삭제되었습니다."}
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    delete_query = get_query("rsvp", "delete",
                             DB_TYPE) if "delete" in DatabaseQueries.RSVP else "DELETE FROM rsvp WHERE id = " + (
        "?" if DB_TYPE == "sqlite" else "%s")

    # RSVP delete 쿼리가 없으면 추가
    if "delete" not in DatabaseQueries.RSVP:
        if DB_TYPE == "postgresql":
            delete_query = "DELETE FROM rsvp WHERE id = %s"
        else:
            delete_query = "DELETE FROM rsvp WHERE id = ?"

    cursor.execute(delete_query, (entry_id,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "RSVP가 삭제되었습니다."}


@router.delete("/api/guestbook/{entry_id}")
async def delete_admin_guestbook(
        entry_id: int,
        request: Request,
        admin_user: str = Depends(get_current_admin)
):
    """Delete guestbook entry (admin only).

    Permanently removes a guestbook entry. No password required for admin.

    Args:
        entry_id (int): ID of the guestbook entry to delete
        request (Request): FastAPI request object
        admin_user (str): Authenticated admin username

    Returns:
        dict: {"status": "success", "message": "방명록이 삭제되었습니다."}
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    delete_query = get_query("guestbook", "delete", DB_TYPE)
    cursor.execute(delete_query, (entry_id,))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "방명록이 삭제되었습니다."}