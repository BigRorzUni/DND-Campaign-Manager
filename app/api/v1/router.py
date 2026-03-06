from fastapi import APIRouter
from app.api.v1.routes import campaigns, sessions

router = APIRouter()
router.include_router(campaigns.router)
router.include_router(sessions.router)