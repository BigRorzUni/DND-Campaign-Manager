from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.character_repo import CharacterRepo
from app.schemas.character_equipment import (
    CharacterEquipmentCreate,
    CharacterKnownEquipmentOut,
)
from app.services.equipment_dataset import EquipmentDatasetService

router = APIRouter(tags=["character-equipment"])
character_repo = CharacterRepo()


def build_equipment_out(equipment: dict) -> CharacterKnownEquipmentOut:
    summary = EquipmentDatasetService.to_summary(equipment)
    return CharacterKnownEquipmentOut(
        equipment_index=summary["api_index"],
        equipment_name_snapshot=summary["name"],
        category=summary.get("category"),
        weapon_category=summary.get("weapon_category"),
        damage_dice=summary.get("damage_dice"),
        damage_type=summary.get("damage_type"),
        armor_category=summary.get("armor_category"),
        armor_class_base=summary.get("armor_class_base"),
        brief_description=summary.get("brief_description"),
    )


@router.get(
    "/characters/{character_id}/equipment",
    response_model=list[CharacterKnownEquipmentOut],
)
def list_character_equipment(
    character_id: int,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    results: list[CharacterKnownEquipmentOut] = []

    for equipment_index in character.equipment_indices or []:
        try:
            equipment = EquipmentDatasetService.get_equipment(equipment_index)
        except Exception:
            continue

        results.append(build_equipment_out(equipment))

    results.sort(key=lambda e: e.equipment_name_snapshot.lower())
    return results


@router.post(
    "/characters/{character_id}/equipment",
    response_model=list[CharacterKnownEquipmentOut],
    status_code=status.HTTP_201_CREATED,
)
def add_character_equipment(
    character_id: int,
    payload: CharacterEquipmentCreate,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    try:
        equipment = EquipmentDatasetService.get_equipment(payload.equipment_index)
    except Exception:
        raise HTTPException(status_code=404, detail="Equipment not found")

    current = list(character.equipment_indices or [])

    if payload.equipment_index in current:
        raise HTTPException(status_code=400, detail="Character already has this equipment")

    current.append(payload.equipment_index)
    character.equipment_indices = current
    db.commit()
    db.refresh(character)

    return list_character_equipment(character_id, db)


@router.delete(
    "/characters/{character_id}/equipment/{equipment_index}",
    response_model=list[CharacterKnownEquipmentOut],
)
def delete_character_equipment(
    character_id: int,
    equipment_index: str,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    current = list(character.equipment_indices or [])

    if equipment_index not in current:
        raise HTTPException(status_code=404, detail="Character does not have this equipment")

    current.remove(equipment_index)
    character.equipment_indices = current
    db.commit()
    db.refresh(character)

    return list_character_equipment(character_id, db)