from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.character import Character
from app.repositories.resource_state_repo import ResourceStateRepo
from app.schemas.resource_state import (
    CharacterResourceStateCreate,
    CharacterResourceStateOut,
    CharacterResourceStateUpdate,
)

router = APIRouter(tags=["resource_states"])
resource_state_repo = ResourceStateRepo()


@router.post(
    "/characters/{character_id}/resource-state",
    response_model=CharacterResourceStateOut,
    status_code=status.HTTP_201_CREATED,
)
def create_resource_state(
    character_id: int,
    payload: CharacterResourceStateCreate,
    db: DbSession = Depends(get_db),
):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    existing = resource_state_repo.get_by_character_id(db, character_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Resource state already exists for this character",
        )

    return resource_state_repo.create(
        db,
        character_id=character_id,
        current_hp=payload.current_hp,
        spell_slots_1_current=payload.spell_slots_1_current,
        spell_slots_1_max=payload.spell_slots_1_max,
        spell_slots_2_current=payload.spell_slots_2_current,
        spell_slots_2_max=payload.spell_slots_2_max,
        spell_slots_3_current=payload.spell_slots_3_current,
        spell_slots_3_max=payload.spell_slots_3_max,
        hit_dice_current=payload.hit_dice_current,
        hit_dice_max=payload.hit_dice_max,
    )


@router.get(
    "/characters/{character_id}/resource-state",
    response_model=CharacterResourceStateOut,
)
def get_resource_state(character_id: int, db: DbSession = Depends(get_db)):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    obj = resource_state_repo.get_by_character_id(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Resource state not found")

    return obj


@router.put(
    "/characters/{character_id}/resource-state",
    response_model=CharacterResourceStateOut,
)
def update_resource_state(
    character_id: int,
    payload: CharacterResourceStateUpdate,
    db: DbSession = Depends(get_db),
):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    obj = resource_state_repo.get_by_character_id(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Resource state not found")

    return resource_state_repo.update(
        db,
        obj,
        current_hp=payload.current_hp,
        spell_slots_1_current=payload.spell_slots_1_current,
        spell_slots_1_max=payload.spell_slots_1_max,
        spell_slots_2_current=payload.spell_slots_2_current,
        spell_slots_2_max=payload.spell_slots_2_max,
        spell_slots_3_current=payload.spell_slots_3_current,
        spell_slots_3_max=payload.spell_slots_3_max,
        hit_dice_current=payload.hit_dice_current,
        hit_dice_max=payload.hit_dice_max,
    )