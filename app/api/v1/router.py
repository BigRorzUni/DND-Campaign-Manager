from fastapi import APIRouter
from app.api.v1.routes import (
    campaigns,
    character_spells,
    sessions,
    encounters,
    events,
    participants,
    characters,
    analytics,
    ai_review,
    character_spells,
    spells,
    monsters,
)

router = APIRouter()
router.include_router(campaigns.router)
router.include_router(sessions.router)
router.include_router(encounters.router)
router.include_router(events.router)
router.include_router(participants.router)
router.include_router(characters.router)
router.include_router(analytics.router, prefix="/analytics")
router.include_router(ai_review.router)
router.include_router(character_spells.router)
router.include_router(spells.router)
router.include_router(monsters.router)