from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.participant_action_repo import ParticipantActionRepo
from app.repositories.participant_repo import ParticipantRepo
from app.schemas.participant_actions import (
    ParticipantActionCreate,
    ParticipantActionUpdate,
    ParticipantActionOut,
)


router = APIRouter(prefix="/participants/{participant_id}/actions", tags=["participant-actions"])

participant_action_repo = ParticipantActionRepo()
participant_repo = ParticipantRepo()


@router.get("", response_model=list[ParticipantActionOut])
def list_participant_actions(
    participant_id: int,
    db: DbSession = Depends(get_db),
):
    participant = participant_repo.get(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return participant_action_repo.list_for_participant(db, participant_id)


@router.post("", response_model=ParticipantActionOut, status_code=status.HTTP_201_CREATED)
def create_participant_action(
    participant_id: int,
    payload: ParticipantActionCreate,
    db: DbSession = Depends(get_db),
):
    participant = participant_repo.get(db, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return participant_action_repo.create(
        db,
        participant_id=participant_id,
        name=payload.name,
        action_type=payload.action_type,
        description=payload.description,
        attack_bonus=payload.attack_bonus,
        average_damage=payload.average_damage,
        damage_dice=payload.damage_dice,
        damage_type=payload.damage_type,
        range_text=payload.range_text,
        is_dataset_imported=False,
        notes=payload.notes,
    )


@router.put("/{action_id}", response_model=ParticipantActionOut)
def update_participant_action(
    participant_id: int,
    action_id: int,
    payload: ParticipantActionUpdate,
    db: DbSession = Depends(get_db),
):
    obj = participant_action_repo.get(db, action_id)

    if not obj or obj.participant_id != participant_id:
        raise HTTPException(status_code=404, detail="Participant action not found")

    fields = payload.model_dump(exclude_unset=True)

    return participant_action_repo.update(db, obj, **fields)


@router.delete("/{action_id}", status_code=204)
def delete_participant_action(
    participant_id: int,
    action_id: int,
    db: DbSession = Depends(get_db),
):
    obj = participant_action_repo.get(db, action_id)

    if not obj or obj.participant_id != participant_id:
        raise HTTPException(status_code=404, detail="Participant action not found")

    participant_action_repo.delete(db, obj)