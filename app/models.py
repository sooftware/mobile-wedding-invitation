"""Pydantic Models for API Request/Response.

Data validation models using Pydantic for:
- Guestbook entries (create, update, delete, verify)
- RSVP responses
- Other API request/response structures

These models provide:
- Automatic validation of incoming data
- Type checking and coercion
- Documentation for API endpoints
- Serialization/deserialization

All models inherit from pydantic.BaseModel and use type hints
for automatic validation.
"""

from pydantic import BaseModel
from typing import Optional


# 방명록 모델
class GuestbookEntry(BaseModel):
    name: str
    message: str
    password: str


class GuestbookUpdate(BaseModel):
    id: int
    name: str
    message: str
    password: str


class DeleteGuestbookEntry(BaseModel):
    id: int
    password: str


class PasswordVerify(BaseModel):
    id: int
    password: str


# RSVP 모델
class RSVPEntry(BaseModel):
    which_side: str
    can_attend: str
    guest_name: str
    phone_number: Optional[str] = None
    companion_count: Optional[int] = 1
    meal_attendance: Optional[str] = None