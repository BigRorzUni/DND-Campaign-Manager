from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.character import Character
from app.schemas.character_spells import CharacterSpellCreate, CharacterSpellOut
from app.repositories.character_spell_repo import CharacterSpellRepo
from app.services.spell_dataset import SpellDatasetService


router = APIRouter(prefix="/characters/{character_id}/spells", tags=["character-spells"])


@router.post("", response_model=CharacterSpellOut)
def add_character_spell(
    character_id: int,
    payload: CharacterSpellCreate,
    db: DbSession = Depends(get_db)
):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    spell = SpellDatasetService.get_spell(payload.spell_index)

    if not spell:
        raise HTTPException(status_code=404, detail="Spell not found in dataset")

    spell_level = spell.get("level")
    if spell_level is None:
        raise HTTPException(status_code=400, detail="Spell level unavailable")

    if character.level is not None and spell_level > character.level:
        raise HTTPException(
            status_code=400,
            detail="Character level is too low for this spell"
        )

    desc = spell.get("desc", [])
    brief_description = desc[0] if isinstance(desc, list) and desc else None

    return CharacterSpellRepo.create(
        db,
        character_id=character_id,
        spell_index=spell["index"],
        spell_name_snapshot=spell["name"],
        spell_level=spell_level,
        brief_description=brief_description,
        notes=payload.notes
    )


@router.get("", response_model=list[CharacterSpellOut])
def list_character_spells(
    character_id: int,
    db: DbSession = Depends(get_db)
):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return CharacterSpellRepo.list_for_character(db, character_id)


@router.delete("/{spell_id}", status_code=204)
def remove_character_spell(
    character_id: int,
    spell_id: int,
    db: DbSession = Depends(get_db)
):
    obj = CharacterSpellRepo.get(db, spell_id)

    if not obj or obj.character_id != character_id:
        raise HTTPException(status_code=404, detail="Character spell not found")

    CharacterSpellRepo.delete(db, obj)