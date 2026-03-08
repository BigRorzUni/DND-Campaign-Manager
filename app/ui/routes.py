from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )

@router.get("/campaigns/{campaign_id}/view", response_class=HTMLResponse)
def campaign_view(request: Request, campaign_id: int):
    return templates.TemplateResponse(
        request=request,
        name="campaign.html",
        context={"campaign_id": campaign_id}
    )

@router.get("/sessions/{session_id}/view", response_class=HTMLResponse)
def session_view(request: Request, session_id: int):
    return templates.TemplateResponse(
        "session.html",
        {
            "request": request,
            "session_id": session_id
        }
    )

@router.get("/encounters/{encounter_id}/view", response_class=HTMLResponse)
def encounter_view(request: Request, encounter_id: int):
    return templates.TemplateResponse(
        "encounter.html",
        {
            "request": request,
            "encounter_id": encounter_id
        }
    )