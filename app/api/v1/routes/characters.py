from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.campaign_repo import CampaignRepo
from app.repositories.character_repo import CharacterRepo
from app.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate
from app.repositories.resource_state_repo import ResourceStateRepo

router = APIRouter(tags=["characters"])
campaign_repo = CampaignRepo()
character_repo = CharacterRepo()
resource_state_repo = ResourceStateRepo()

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
        notes=payload.notes,
    )

    # initialise resource state automatically
    initial_hp = payload.current_hp if payload.current_hp is not None else payload.max_hp

    resource_state_repo.create(
        db,
        character_id=character.id,
        current_hp=initial_hp,
        spell_slots_1_current=0,
        spell_slots_1_max=0,
        spell_slots_2_current=0,
        spell_slots_2_max=0,
        spell_slots_3_current=0,
        spell_slots_3_max=0,
        hit_dice_current=payload.level if payload.level is not None else 0,
        hit_dice_max=payload.level if payload.level is not None else 0,
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
        name=payload.name,
        role=payload.role,
        class_name=payload.class_name,
        level=payload.level,
        max_hp=payload.max_hp,
        current_hp=payload.current_hp,
        armor_class=payload.armor_class,
        notes=payload.notes,
    )


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: DbSession = Depends(get_db)):
    obj = character_repo.get(db, character_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Character not found")
    character_repo.delete(db, obj)