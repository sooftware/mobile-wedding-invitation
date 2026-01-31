"""Statistics and Visitor Tracking Router.

Tracks and reports visitor statistics for the wedding invitation site.

Features:
    - Records every page visit (including repeat visits)
    - Tracks total visit count
    - IP address and user agent logging
    - Admin-only detailed statistics
    - Public summary statistics

Routes:
    GET /api/visitor-stats: Public stats (today/total counts)
    GET /admin/api/visitor-daily: Detailed daily stats (admin only)

Internal Functions:
    record_visitor(): Records each page visit with IP and user agent
"""

import logging
from datetime import date
from fastapi import APIRouter, Request, Depends
from app.core.database import get_db_connection, DB_TYPE, DATABASE_URL
from app.core.utils import get_client_ip
from app.database.queries import get_query
from app.admin.auth import get_current_admin

router = APIRouter(tags=["stats"])
logger = logging.getLogger(__name__)


async def record_visitor(request: Request):
    """Record visitor information for statistics.

    Logs visitor IP address and user agent for every visit.
    Records every page visit, allowing multiple visits from same IP.

    Args:
        request (Request): FastAPI Request object

    Note:
        - Extracts IP considering proxy headers (X-Forwarded-For)
        - Truncates user agent to 500 characters
        - Records every visit (no duplicate prevention)
        - Errors are logged but don't break the application
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today()
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")[:500]  # 500자 제한

        query = get_query("visitor_stats", "insert", DB_TYPE)
        cursor.execute(query, (today, ip_address, user_agent))

        conn.commit()
        conn.close()

        logger.info(f"✅ 방문자 기록: {ip_address}")
    except Exception as e:
        logger.error(f"방문자 기록 실패: {e}")


@router.get("/api/visitor-stats")
async def get_visitor_stats():
    """Get public visitor statistics.

    Returns summary of today's total visits and all-time total visits.
    Counts every visit, not unique visitors.
    This endpoint is public and doesn't require authentication.

    Returns:
        dict: {
            "today": int (total visits today),
            "total": int (all-time total visits)
        }

    Note:
        Returns zeros on error to prevent breaking frontend display
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 오늘 방문자
        cursor.execute(get_query("visitor_stats", "count_today", DB_TYPE))
        today_result = cursor.fetchone()

        if DATABASE_URL:
            today_count = today_result['count'] if today_result else 0
        else:
            today_count = today_result[0] if today_result else 0

        # 총 방문자
        cursor.execute(get_query("visitor_stats", "count_total"))
        total_result = cursor.fetchone()

        if DATABASE_URL:
            total_count = total_result['total_count'] if total_result else 0
        else:
            total_count = total_result[0] if total_result else 0

        conn.close()

        return {
            "today": today_count,
            "total": total_count
        }
    except Exception as e:
        logger.error(f"방문자 통계 조회 실패: {e}")
        return {"today": 0, "total": 0}


@router.get("/admin/api/visitor-daily")
async def get_daily_visitor_stats(
        request: Request,
        admin_user: str = Depends(get_current_admin)
):
    """Get detailed daily visitor statistics (admin only).

    Returns the last 30 days of visitor data with unique visitors
    and total visits per day. Requires admin authentication.

    Args:
        request (Request): FastAPI request object
        admin_user (str): Authenticated admin username

    Returns:
        dict: {
            "stats": list of daily stat dicts with:
                - date: ISO format date string
                - unique_visitors: count of unique IPs
                - total_visits: total visit count
        }

    Note:
        Returns empty list on error to prevent breaking admin dashboard
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(get_query("visitor_stats", "daily_stats"))
        rows = cursor.fetchall()

        stats = []
        for row in rows:
            if DATABASE_URL:
                stats.append({
                    "date": row['visit_date'].isoformat() if hasattr(row['visit_date'], 'isoformat') else str(
                        row['visit_date']),
                    "unique_visitors": row['unique_visitors'],
                    "total_visits": row['total_visits']
                })
            else:
                stats.append({
                    "date": row[0],
                    "unique_visitors": row[1],
                    "total_visits": row[2]
                })

        conn.close()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"일별 통계 조회 실패: {e}")
        return {"stats": []}