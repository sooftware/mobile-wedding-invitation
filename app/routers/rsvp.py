"""RSVP Router.

Handles wedding attendance responses from guests.
Stores information about which side (bride/groom), attendance status,
guest details, and number of companions.

Routes:
    POST /api/rsvp: Submit RSVP response
"""

import logging
from fastapi import APIRouter, HTTPException
from app.core.database import get_db_connection, DB_TYPE
from app.database.queries import get_query
from app.models import RSVPEntry

router = APIRouter(prefix="/api/rsvp", tags=["rsvp"])
logger = logging.getLogger(__name__)


@router.post("")
async def submit_rsvp_api(entry: RSVPEntry):
    """Submit RSVP response (JSON API).

    Records guest attendance intention with optional phone number
    and companion count.

    Args:
        entry (RSVPEntry): RSVP data containing:
            - which_side: 'groom' or 'bride'
            - can_attend: 'yes' or 'no'
            - guest_name: Name of the guest
            - phone_number: Optional contact number
            - companion_count: Number of people attending (default: 1)

    Returns:
        dict: {
            "status": "success",
            "message": "참석 여부가 성공적으로 전달되었습니다."
        }

    Raises:
        HTTPException 500: If database operation fails
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = get_query("rsvp", "insert", DB_TYPE)
        cursor.execute(query, (
            entry.which_side,
            entry.can_attend,
            entry.guest_name,
            entry.phone_number or '',
            entry.companion_count or 1,
            entry.meal_attendance or ''
        ))

        conn.commit()
        conn.close()

        logger.info(f"✅ RSVP 저장 완료: {entry.guest_name} ({entry.companion_count}명)")

        return {
            "status": "success",
            "message": "참석 여부가 성공적으로 전달되었습니다."
        }

    except Exception as e:
        logger.error(f"❌ RSVP 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))