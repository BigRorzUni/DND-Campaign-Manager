from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.character import Character
from app.models.encounter import Encounter
from app.models.session import Session
from app.repositories.participant_repo import ParticipantRepo
from app.models.encounter_participant_state import EncounterParticipantState
from app.schemas.participant import EncounterParticipantCreate, EncounterParticipantOut

router = APIRouter(tags=["participants"])
participant_repo = ParticipantRepo()


@router.post(
    "/encounters/{encounter_id}/participants",
    response_model=EncounterParticipantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_participant(
    encounter_id: int,
    payload: EncounterParticipantCreate,
    db: DbSession = Depends(get_db),
):
    encounter = db.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    character = db.get(Character, payload.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # make sure the character belongs to the same campaign as the encounter
    encounter_session = db.get(Session, encounter.session_id)
    if not encounter_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if character.campaign_id != encounter_session.campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Character does not belong to the same campaign as this encounter",
        )

    return participant_repo.create(
        db,
        encounter_id=encounter_id,
        character_id=payload.character_id,
        starting_hp=payload.starting_hp,
        starting_hp_percent=payload.starting_hp_percent,
        spell_slots_1_start=payload.spell_slots_1_start,
        spell_slots_2_start=payload.spell_slots_2_start,
        spell_slots_3_start=payload.spell_slots_3_start,
        hit_dice_start=payload.hit_dice_start,
        notes=payload.notes,
    )

@router.get(
    "/encounters/{encounter_id}/participants",
    response_model=list[EncounterParticipantOut],
)
def list_participants(encounter_id: int, db: DbSession = Depends(get_db)):
    rows = (
        db.query(EncounterParticipantState, Character)
        .join(Character, Character.id == EncounterParticipantState.character_id)
        .filter(EncounterParticipantState.encounter_id == encounter_id)
        .all()
    )

    results = []

    for participant, character in rows:
        results.append(
            EncounterParticipantOut(
                id=participant.id,
                encounter_id=participant.encounter_id,
                character_id=participant.character_id,
                character_name=character.name,
                character_class=character.class_name,
                character_level=character.level,
                starting_hp=participant.starting_hp,
                starting_hp_percent=participant.starting_hp_percent,
                spell_slots_1_start=participant.spell_slots_1_start,
                spell_slots_2_start=participant.spell_slots_2_start,
                spell_slots_3_start=participant.spell_slots_3_start,
                hit_dice_start=participant.hit_dice_start,
                notes=participant.notes,
            )
        )

    return results


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(participant_id: int, db: DbSession = Depends(get_db)):
    obj = participant_repo.get(db, participant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Participant not found")
    participant_repo.delete(db, obj)