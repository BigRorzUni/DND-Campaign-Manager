from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.encounter_repo import EncounterRepo
from app.repositories.event_repo import EventRepo
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.event_service import EventService

router = APIRouter(tags=["events"])
encounter_repo = EncounterRepo()
event_repo = EventRepo()
event_service = EventService()


@router.post(
    "/encounters/{encounter_id}/events",
    response_model=EventOut,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    encounter_id: int,
    payload: EventCreate,
    db: DbSession = Depends(get_db)
):
    encounter = encounter_repo.get(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return event_service.create_event(
        db,
        encounter_id=encounter_id,
        kind=payload.kind,
        source=payload.source,
        target=payload.target,
        source_character_id=payload.source_character_id,
        target_character_id=payload.target_character_id,
        amount=payload.amount,
        slot_level_used=payload.slot_level_used,
        slots_consumed=payload.slots_consumed,
        detail=payload.detail,
    )


@router.get("/encounters/{encounter_id}/events", response_model=list[EventOut])
def list_events(encounter_id: int, db: DbSession = Depends(get_db)):
    encounter = encounter_repo.get(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return event_repo.list_for_encounter(db, encounter_id)


@router.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: DbSession = Depends(get_db)):
    obj = event_repo.get(db, event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")
    return obj


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: DbSession = Depends(get_db)):
    obj = event_repo.get(db, event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")
    event_repo.delete(db, obj)