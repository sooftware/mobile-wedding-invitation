"""Home Router.

Handles the main landing page of the wedding invitation.
Records visitor statistics and renders the homepage template
with wedding configuration and map integration.

Routes:
    GET /: Main wedding invitation page
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.config import KAKAO_APP_KEY, config
from app.routers.stats import record_visitor

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main wedding invitation page.

    Records visitor statistics and returns the homepage template
    with wedding configuration and Kakao map integration.

    Args:
        request (Request): FastAPI request object

    Returns:
        HTMLResponse: Rendered index.html template

    Template Context:
        - request: FastAPI request object
        - kakao_app_key: Kakao API key for maps
        - config: Wedding configuration (couple info, venue, etc.)
    """
    # 방문자 기록
    await record_visitor(request)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "kakao_app_key": KAKAO_APP_KEY,
        "config": config
    })