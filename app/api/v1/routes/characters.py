from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.campaign_repo import CampaignRepo
from app.repositories.character_repo import CharacterRepo
from app.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate

router = APIRouter(tags=["characters"])
campaign_repo = CampaignRepo()
character_repo = CharacterRepo()

@router.post(
    "/campaigns/{campaign_id}/characters",
    response_model=CharacterOut,
    status_code=status.HTTP_201_CREATED,
)
def create_character(
    campaign_id: int,
    payload: CharacterCreate,
    db: DbSession = Depends(get_db),
):
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    character = character_repo.create(
        db,
        campaign_id=campaign_id,
        name=payload.name,
        role=payload.role,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        armor_class=payload.armor_class,
        spell_indices=payload.spell_indices,
        equipment_indices=payload.equipment_indices,
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

    return character


@router.get("/campaigns/{campaign_id}/characters", response_model=list[CharacterOut])
def list_characters(campaign_id: int, db: DbSession = Depends(get_db)):
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return character_repo.list_for_campaign(db, campaign_id)


@router.get("/characters/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, db: DbSession = Depends(get_db)):
    obj = character_repo.get(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Character not found")
    return obj


@router.put("/characters/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: int,
    payload: CharacterUpdate,
    db: DbSession = Depends(get_db),
):
    obj = character_repo.get(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Character not found")

    return character_repo.update(
        db,
        obj,
        name=payload.name if payload.name is not None else obj.name,
        role=payload.role if payload.role is not None else obj.role,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        armor_class=payload.armor_class,
        spell_indices=payload.spell_indices if payload.spell_indices is not None else obj.spell_indices,
        equipment_indices=payload.equipment_indices if payload.equipment_indices is not None else obj.equipment_indices,
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


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: DbSession = Depends(get_db)):
    obj = character_repo.get(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Character not found")
    character_repo.delete(db, obj)