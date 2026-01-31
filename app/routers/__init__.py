"""Routers Module.

Collection of API routers organized by feature:
- home: Main landing page
- guestbook: Guest message management
- rsvp: Wedding attendance responses
- admin: Administrative functions
- chatbot: AI-powered Q&A
- stats: Visitor tracking and statistics

Each router is a separate module with its own endpoints and logic.
"""

from app.routers import home, guestbook, rsvp, admin, chatbot, stats

__all__ = ['home', 'guestbook', 'rsvp', 'admin', 'chatbot', 'stats']