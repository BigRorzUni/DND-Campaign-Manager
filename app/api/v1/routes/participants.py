from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.character import Character
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.session import Session
from app.repositories.participant_repo import ParticipantRepo
from app.schemas.participant import (
    EncounterParticipantCreate,
    EncounterParticipantOut,
    EncounterParticipantUpdate,
)
from app.services.ai_review_service import AiReviewService
from app.services.spell_dataset import SpellDatasetService
from app.repositories.character_spell_repo import CharacterSpellRepo
from app.services.monster_dataset import MonsterDatasetService
from app.repositories.participant_action_repo import ParticipantActionRepo

ai_review_service = AiReviewService()

router = APIRouter(tags=["participants"])
participant_repo = ParticipantRepo()
participant_action_repo = ParticipantActionRepo()


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

        max_hp = payload.max_hp if payload.max_hp is not None else character.max_hp
        current_hp = payload.current_hp if payload.current_hp is not None else max_hp

        participant = participant_repo.create(
            db,
            encounter_id=encounter_id,
            character_id=character.id,
            monster_index=None,
            name=character.name,
            participant_type=payload.participant_type,
            class_name=character.class_name,
            level=character.level,
            max_hp=max_hp,
            current_hp=current_hp,
            initial_current_hp=current_hp,
            armor_class=character.armor_class,
            spell_slots_1=payload.spell_slots_1 if payload.spell_slots_1 is not None else character.spell_slots_1,
            spell_slots_2=payload.spell_slots_2 if payload.spell_slots_2 is not None else character.spell_slots_2,
            spell_slots_3=payload.spell_slots_3 if payload.spell_slots_3 is not None else character.spell_slots_3,
            spell_slots_4=payload.spell_slots_4 if payload.spell_slots_4 is not None else character.spell_slots_4,
            spell_slots_5=payload.spell_slots_5 if payload.spell_slots_5 is not None else character.spell_slots_5,
            spell_slots_6=payload.spell_slots_6 if payload.spell_slots_6 is not None else character.spell_slots_6,
            spell_slots_7=payload.spell_slots_7 if payload.spell_slots_7 is not None else character.spell_slots_7,
            spell_slots_8=payload.spell_slots_8 if payload.spell_slots_8 is not None else character.spell_slots_8,
            spell_slots_9=payload.spell_slots_9 if payload.spell_slots_9 is not None else character.spell_slots_9,
            initial_spell_slots_1=payload.spell_slots_1 if payload.spell_slots_1 is not None else character.spell_slots_1,
            initial_spell_slots_2=payload.spell_slots_2 if payload.spell_slots_2 is not None else character.spell_slots_2,
            initial_spell_slots_3=payload.spell_slots_3 if payload.spell_slots_3 is not None else character.spell_slots_3,
            initial_spell_slots_4=payload.spell_slots_4 if payload.spell_slots_4 is not None else character.spell_slots_4,
            initial_spell_slots_5=payload.spell_slots_5 if payload.spell_slots_5 is not None else character.spell_slots_5,
            initial_spell_slots_6=payload.spell_slots_6 if payload.spell_slots_6 is not None else character.spell_slots_6,
            initial_spell_slots_7=payload.spell_slots_7 if payload.spell_slots_7 is not None else character.spell_slots_7,
            initial_spell_slots_8=payload.spell_slots_8 if payload.spell_slots_8 is not None else character.spell_slots_8,
            initial_spell_slots_9=payload.spell_slots_9 if payload.spell_slots_9 is not None else character.spell_slots_9,
            notes=payload.notes,
        )

        ai_review_service.mark_encounter_review_stale(db, encounter_id)
        return participant

    if payload.monster_index:
        monster = MonsterDatasetService.get_monster(payload.monster_index)
        if not monster:
            raise HTTPException(status_code=404, detail="Monster not found")

        max_hp = payload.max_hp if payload.max_hp is not None else monster.get("hit_points")
        current_hp = payload.current_hp if payload.current_hp is not None else max_hp

        armor_class = None
        raw_ac = monster.get("armor_class")
        if isinstance(raw_ac, list) and raw_ac:
            armor_class = raw_ac[0].get("value")
        elif isinstance(raw_ac, int):
            armor_class = raw_ac

        monster_type = monster.get("type")
        if isinstance(monster_type, dict):
            monster_type = monster_type.get("name")

        participant = participant_repo.create(
            db,
            encounter_id=encounter_id,
            character_id=None,
            monster_index=monster["index"],
            name=monster["name"],
            participant_type=payload.participant_type,
            class_name=monster_type,
            level=payload.level,
            max_hp=max_hp,
            current_hp=current_hp,
            initial_current_hp=current_hp,
            armor_class=armor_class,
            spell_slots_1=payload.spell_slots_1,
            spell_slots_2=payload.spell_slots_2,
            spell_slots_3=payload.spell_slots_3,
            spell_slots_4=payload.spell_slots_4,
            spell_slots_5=payload.spell_slots_5,
            spell_slots_6=payload.spell_slots_6,
            spell_slots_7=payload.spell_slots_7,
            spell_slots_8=payload.spell_slots_8,
            spell_slots_9=payload.spell_slots_9,
            initial_spell_slots_1=payload.spell_slots_1,
            initial_spell_slots_2=payload.spell_slots_2,
            initial_spell_slots_3=payload.spell_slots_3,
            initial_spell_slots_4=payload.spell_slots_4,
            initial_spell_slots_5=payload.spell_slots_5,
            initial_spell_slots_6=payload.spell_slots_6,
            initial_spell_slots_7=payload.spell_slots_7,
            initial_spell_slots_8=payload.spell_slots_8,
            initial_spell_slots_9=payload.spell_slots_9,
            notes=payload.notes,
        )

        action_rows = MonsterDatasetService.extract_action_rows(monster, participant.id)
        if action_rows:
            participant_action_repo.create_many(db, action_rows)

        ai_review_service.mark_encounter_review_stale(db, encounter_id)
        return participant

    if not payload.name:
        raise HTTPException(
            status_code=400,
            detail="Name is required for non-character participants",
        )

    current_hp = payload.current_hp if payload.current_hp is not None else payload.max_hp

    participant = participant_repo.create(
        db,
        encounter_id=encounter_id,
        character_id=None,
        monster_index=None,
        name=payload.name,
        participant_type=payload.participant_type,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=current_hp,
        initial_current_hp=current_hp,
        armor_class=payload.armor_class,
        spell_slots_1=payload.spell_slots_1,
        spell_slots_2=payload.spell_slots_2,
        spell_slots_3=payload.spell_slots_3,
        spell_slots_4=payload.spell_slots_4,
        spell_slots_5=payload.spell_slots_5,
        spell_slots_6=payload.spell_slots_6,
        spell_slots_7=payload.spell_slots_7,
        spell_slots_8=payload.spell_slots_8,
        spell_slots_9=payload.spell_slots_9,
        initial_spell_slots_1=payload.spell_slots_1,
        initial_spell_slots_2=payload.spell_slots_2,
        initial_spell_slots_3=payload.spell_slots_3,
        initial_spell_slots_4=payload.spell_slots_4,
        initial_spell_slots_5=payload.spell_slots_5,
        initial_spell_slots_6=payload.spell_slots_6,
        initial_spell_slots_7=payload.spell_slots_7,
        initial_spell_slots_8=payload.spell_slots_8,
        initial_spell_slots_9=payload.spell_slots_9,
        notes=payload.notes,
    )

    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return participant


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

    updated = participant_repo.update(
        db,
        obj,
        character_id=payload.character_id,
        monster_index=payload.monster_index,
        name=payload.name,
        participant_type=payload.participant_type,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        armor_class=payload.armor_class,
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

    ai_review_service.mark_encounter_review_stale(db, updated.encounter_id)
    return updated


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(participant_id: int, db: DbSession = Depends(get_db)):
    obj = participant_repo.get(db, participant_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Participant not found")

    encounter_id = obj.encounter_id
    participant_repo.delete(db, obj)
    ai_review_service.mark_encounter_review_stale(db, encounter_id)
    return None


@router.get("/participants/{participant_id}/spells")
def get_participant_spells(participant_id: int, db: DbSession = Depends(get_db)):
    participant = db.get(EncounterParticipant, participant_id)

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    if participant.character_id:
        return CharacterSpellRepo.list_for_character(db, participant.character_id)

    return SpellDatasetService.list_spells()