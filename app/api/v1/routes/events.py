from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.event_repo import event_repo
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.ai_review_service import AiReviewService
from app.services.encounter_state_service import recalculate_encounter_state
from app.services.spell_dataset import SpellDatasetService

router = APIRouter(tags=["events"])
ai_review_service = AiReviewService()


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
    spell_index = payload.spell_index
    spell_name_snapshot = None

    if spell_index:
        spell = SpellDatasetService.get_spell(spell_index)

        if not spell:
            raise HTTPException(status_code=404, detail="Spell not found")

        spell_name_snapshot = spell["name"]
        
    event = event_repo.create(
        db,
        encounter_id=encounter_id,
        kind=payload.kind,
        source_participant_id=payload.source_participant_id,
        target_participant_id=payload.target_participant_id,
        amount=payload.amount,
        spell_slots_consumed=payload.spell_slots_consumed,
        spell_slot_level_used=payload.spell_slot_level_used,
        detail=payload.detail,
        spell_index=spell_index,
        spell_name_snapshot=spell_name_snapshot,
    )

    recalculate_encounter_state(db, encounter_id)
    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return event


@router.get(
    "/encounters/{encounter_id}/events",
    response_model=list[EventOut],
)
def list_events(encounter_id: int, db: DbSession = Depends(get_db)):
    return event_repo.list_for_encounter(db, encounter_id)


@router.put(
    "/events/{event_id}",
    response_model=EventOut,
)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: DbSession = Depends(get_db),
):
    event = event_repo.get(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    updated = event_repo.update(
        db,
        event,
        kind=payload.kind if payload.kind is not None else event.kind,
        source_participant_id=payload.source_participant_id,
        target_participant_id=payload.target_participant_id,
        amount=payload.amount,
        spell_slots_consumed=payload.spell_slots_consumed,
        spell_slot_level_used=payload.spell_slot_level_used,
        detail=payload.detail,
    )

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
        raise HTTPException(status_code=404, detail="Event not found")

    encounter_id = event.encounter_id
    event_repo.delete(db, event)

    recalculate_encounter_state(db, encounter_id)
    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return None