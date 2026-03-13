from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.schemas.action import ActionOptionOut
from app.services.action_catalog_service import ActionCatalogService

router = APIRouter(tags=["combat"])
action_catalog_service = ActionCatalogService()


@router.get(
    "/encounters/{encounter_id}/participants/{participant_id}/actions",
    response_model=list[ActionOptionOut],
)
def list_participant_actions(
    encounter_id: int,
    participant_id: int,
    db: DbSession = Depends(get_db),
):
    try:
        return action_catalog_service.list_actions_for_participant(db, participant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))