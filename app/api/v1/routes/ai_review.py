from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.schemas.ai_review import EncounterAiReviewOut
from app.services.ai_review_service import AiReviewService

router = APIRouter(tags=["ai-review"])
ai_review_service = AiReviewService()


@router.get(
    "/encounters/{encounter_id}/ai-review",
    response_model=EncounterAiReviewOut,
)
def encounter_ai_review(
    encounter_id: int,
    refresh: bool = Query(default=False),
    db: DbSession = Depends(get_db),
):
    return ai_review_service.get_or_generate_review(
        db,
        encounter_id,
        force_refresh=refresh,
    )