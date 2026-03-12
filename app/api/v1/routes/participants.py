from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.character import Character
from app.models.encounter import Encounter
from app.models.session import Session
from app.repositories.participant_repo import ParticipantRepo
from app.schemas.participant import EncounterParticipantCreate, EncounterParticipantOut, EncounterParticipantUpdate
from app.services.ai_review_service import AiReviewService
from app.services.spell_dataset import SpellDatasetService
from app.repositories.character_spell_repo import CharacterSpellRepo

ai_review_service = AiReviewService()

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

    encounter_session = db.get(Session, encounter.session_id)
    if not encounter_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if payload.character_id is not None:
        character = db.get(Character, payload.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        if character.campaign_id != encounter_session.campaign_id:
            raise HTTPException(
                status_code=400,
                detail="Character does not belong to the same campaign as this encounter",
            )

        participant = participant_repo.create(
            db,
            encounter_id=encounter_id,
            character_id=character.id,
            name=character.name,
            participant_type=payload.participant_type,
            class_name=character.class_name,
            level=character.level,
            max_hp=payload.max_hp if payload.max_hp is not None else character.max_hp,
            current_hp=payload.current_hp,
            spell_slots_1=payload.spell_slots_1 if payload.spell_slots_1 is not None else character.spell_slots_1,
            spell_slots_2=payload.spell_slots_2 if payload.spell_slots_2 is not None else character.spell_slots_2,
            spell_slots_3=payload.spell_slots_3 if payload.spell_slots_3 is not None else character.spell_slots_3,
            spell_slots_4=payload.spell_slots_4 if payload.spell_slots_4 is not None else character.spell_slots_4,
            spell_slots_5=payload.spell_slots_5 if payload.spell_slots_5 is not None else character.spell_slots_5,
            spell_slots_6=payload.spell_slots_6 if payload.spell_slots_6 is not None else character.spell_slots_6,
            spell_slots_7=payload.spell_slots_7 if payload.spell_slots_7 is not None else character.spell_slots_7,
            spell_slots_8=payload.spell_slots_8 if payload.spell_slots_8 is not None else character.spell_slots_8,
            spell_slots_9=payload.spell_slots_9 if payload.spell_slots_9 is not None else character.spell_slots_9,
            notes=payload.notes,
        )
        ai_review_service.mark_encounter_review_stale(db, encounter_id)
        return participant

    if not payload.name:
        raise HTTPException(
            status_code=400,
            detail="Name is required for non-character participants",
        )

    return participant_repo.create(
        db,
        encounter_id=encounter_id,
        character_id=None,
        name=payload.name,
        participant_type=payload.participant_type,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        spell_slots_1=payload.spell_slots_1 if payload.spell_slots_1 is not None else character.spell_slots_1,
        spell_slots_2=payload.spell_slots_2 if payload.spell_slots_2 is not None else character.spell_slots_2,
        spell_slots_3=payload.spell_slots_3 if payload.spell_slots_3 is not None else character.spell_slots_3,
        spell_slots_4=payload.spell_slots_4 if payload.spell_slots_4 is not None else character.spell_slots_4,
        spell_slots_5=payload.spell_slots_5 if payload.spell_slots_5 is not None else character.spell_slots_5,
        spell_slots_6=payload.spell_slots_6 if payload.spell_slots_6 is not None else character.spell_slots_6,
        spell_slots_7=payload.spell_slots_7 if payload.spell_slots_7 is not None else character.spell_slots_7,
        spell_slots_8=payload.spell_slots_8 if payload.spell_slots_8 is not None else character.spell_slots_8,
        spell_slots_9=payload.spell_slots_9 if payload.spell_slots_9 is not None else character.spell_slots_9,
        notes=payload.notes,
    )


@router.get(
    "/encounters/{encounter_id}/participants",
    response_model=list[EncounterParticipantOut],
)
def list_participants(encounter_id: int, db: DbSession = Depends(get_db)):
    encounter = db.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    return participant_repo.list_for_encounter(db, encounter_id)

@router.put(
    "/participants/{participant_id}",
    response_model=EncounterParticipantOut,
)
def update_participant(
    participant_id: int,
    payload: EncounterParticipantUpdate,
    db: DbSession = Depends(get_db),
):
    obj = participant_repo.get(db, participant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Participant not found")

    return participant_repo.update(
        db,
        obj,
        character_id=payload.character_id,
        name=payload.name,
        participant_type=payload.participant_type,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        spell_slots_1=payload.spell_slots_1,
        spell_slots_2=payload.spell_slots_2,
        spell_slots_3=payload.spell_slots_3,
        spell_slots_4=payload.spell_slots_4,
        spell_slots_5=payload.spell_slots_5,
        spell_slots_6=payload.spell_slots_6,
        spell_slots_7=payload.spell_slots_7,
        spell_slots_8=payload.spell_slots_8,
        spell_slots_9=payload.spell_slots_9,
        notes=payload.notes,
    )


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(participant_id: int, db: DbSession = Depends(get_db)):
    obj = participant_repo.get(db, participant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Participant not found")
    participant_repo.delete(db, obj)

@router.get("/{participant_id}/spells")
def get_participant_spells(participant_id: int, db: DbSession = Depends(get_db)):

    participant = db.get(EncounterParticipantOut, participant_id)

    if not participant:
        raise HTTPException(404, "Participant not found")

    # party member
    if participant.character_id:
        return CharacterSpellRepo.list_for_character(db, participant.character_id)

    # NPC / enemy → allow searching full dataset
    return SpellDatasetService.list_spells()