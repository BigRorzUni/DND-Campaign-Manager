# app/api/v1/routes/participant_actions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.schemas.participant_actions import ParticipantActionOut
from app.services.participant_action_service import ParticipantActionService

router = APIRouter(tags=["participant-actions"])
service = ParticipantActionService()


@router.get(
    "/encounters/{encounter_id}/participants/{participant_id}/actions",
    response_model=list[ParticipantActionOut],
)
def list_actions(participant_id: int, db: DbSession = Depends(get_db)):
    try:
        return service.list_actions_for_participant(db, participant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))