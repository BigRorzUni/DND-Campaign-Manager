from fastapi import APIRouter
from app.api.v1.routes import campaigns, sessions, encounters, events, analytics, reviews, characters

router = APIRouter()
router.include_router(campaigns.router)
router.include_router(sessions.router)
router.include_router(encounters.router)
router.include_router(events.router)
router.include_router(analytics.router)
router.include_router(reviews.router)
router.include_router(characters.router)