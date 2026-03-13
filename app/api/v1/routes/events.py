from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.event_repo import event_repo
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.ai_review_service import AiReviewService
from app.services.encounter_state_service import recalculate_encounter_state
from app.services.event_service import EventService

router = APIRouter(tags=["events"])
ai_review_service = AiReviewService()
event_service = EventService()


@router.post(
    "/encounters/{encounter_id}/events",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    encounter_id: int,
    payload: EventCreate,
    db: DbSession = Depends(get_db),
):
    event = event_service.create_event(db, encounter_id, payload)
    recalculate_encounter_state(db, encounter_id)
    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return event


@router.get(
    "/encounters/{encounter_id}/events",
    response_model=list[EventOut],
)
def list_events(encounter_id: int, db: DbSession = Depends(get_db)):
    return event_repo.list_for_encounter(db, encounter_id)


@router.put("/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: DbSession = Depends(get_db),
):
    updated = event_service.update_event(db, event_id, payload)
    recalculate_encounter_state(db, updated.encounter_id)
    ai_review_service.mark_encounter_review_stale(db, updated.encounter_id)
    return updated


@router.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(event_id: int, db: DbSession = Depends(get_db)):
    event = event_repo.get(db, event_id)
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")

    encounter_id = event.encounter_id
    event_repo.delete(db, event)

    recalculate_encounter_state(db, encounter_id)
    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return None