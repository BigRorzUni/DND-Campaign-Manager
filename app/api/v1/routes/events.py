from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.encounter_repo import EncounterRepo
from app.repositories.event_repo import EventRepo
from app.schemas.event import EventCreate, EventOut, EventUpdate

router = APIRouter(tags=["events"])
encounter_repo = EncounterRepo()
event_repo = EventRepo()


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

    return event_repo.create(
        db,
        encounter_id=encounter_id,
        kind=payload.kind,
        source=payload.source,
        target=payload.target,
        amount=payload.amount,
        detail=payload.detail
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


@router.put("/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: DbSession = Depends(get_db)
):
    obj = event_repo.get(db, event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")

    return event_repo.update(
        db,
        obj,
        kind=payload.kind,
        source=payload.source,
        target=payload.target,
        amount=payload.amount,
        detail=payload.detail
    )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: DbSession = Depends(get_db)):
    obj = event_repo.get(db, event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")
    event_repo.delete(db, obj)