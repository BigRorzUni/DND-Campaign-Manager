from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.event_repo import event_repo
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.ai_review_service import AiReviewService
from app.services.encounter_state_service import recalculate_encounter_state
from app.services.spell_dataset import SpellDatasetService
from app.models.encounter import Encounter

router = APIRouter(tags=["events"])
ai_review_service = AiReviewService()

def resolve_spell_fields(spell_index: str | None) -> tuple[str | None, str | None, int | None, int | None]:
    if not spell_index:
        return None, None, None, None

    spell = SpellDatasetService.get_spell(spell_index)
    if not spell:
        raise HTTPException(status_code=404, detail="Spell not found in dataset")

    level = spell.get("level")
    name = spell.get("name")
    brief_description = spell.get("brief_description")

    if level is None:
        raise HTTPException(status_code=400, detail="Spell level missing from dataset")

    if level == 0:
        return spell_index, name, brief_description, None

    return spell_index, name, brief_description, level


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
    encounter = db.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    spell_index = None
    spell_name_snapshot = None
    spell_brief_description = None
    spell_slot_level_used = None
    spell_slots_consumed = None

    if payload.spell_index:
        (
            spell_index,
            spell_name_snapshot,
            spell_brief_description,
            spell_slot_level_used,
        ) = resolve_spell_fields(payload.spell_index)

        if spell_slot_level_used is not None:
            spell_slots_consumed = 1

    event = event_repo.create(
        db,
        encounter_id=encounter_id,
        kind=payload.kind,
        source_participant_id=payload.source_participant_id,
        target_participant_id=payload.target_participant_id,
        amount=payload.amount,
        spell_index=spell_index,
        spell_name_snapshot=spell_name_snapshot,
        spell_brief_description=spell_brief_description,
        spell_slots_consumed=spell_slots_consumed,
        spell_slot_level_used=spell_slot_level_used,
        detail=payload.detail,
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


@router.put("/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: DbSession = Depends(get_db),
):
    event = event_repo.get(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    spell_index = None
    spell_name_snapshot = None
    spell_brief_description = None
    spell_slot_level_used = None
    spell_slots_consumed = None

    if payload.spell_index:
        (
            spell_index,
            spell_name_snapshot,
            spell_brief_description,
            spell_slot_level_used,
        ) = resolve_spell_fields(payload.spell_index)

        if spell_slot_level_used is not None:
            spell_slots_consumed = 1

    updated = event_repo.update(
        db,
        event,
        kind=payload.kind,
        source_participant_id=payload.source_participant_id,
        target_participant_id=payload.target_participant_id,
        amount=payload.amount,
        spell_index=spell_index,
        spell_name_snapshot=spell_name_snapshot,
        spell_brief_description=spell_brief_description,
        spell_slots_consumed=spell_slots_consumed,
        spell_slot_level_used=spell_slot_level_used,
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