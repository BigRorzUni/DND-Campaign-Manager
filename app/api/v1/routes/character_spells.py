from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.character_repo import CharacterRepo
from app.schemas.character_spell import CharacterSpellCreate, CharacterKnownSpellOut
from app.services.spell_dataset import SpellDatasetService

router = APIRouter(tags=["character-spells"])
character_repo = CharacterRepo()

def character_has_slot_for_spell_level(character, spell_level: int) -> bool:
    if spell_level == 0:
        return True

    if spell_level < 1 or spell_level > 9:
        return False

    slot_value = getattr(character, f"spell_slots_{spell_level}", None)
    return slot_value is not None and slot_value > 0

def spell_allowed_for_class(spell: dict, class_name: str | None) -> bool:
    if not class_name:
        return False

    spell_classes = [
        cls.get("name", "").strip().lower()
        for cls in (spell.get("classes") or [])
        if cls.get("name")
    ]

    return class_name.strip().lower() in spell_classes


@router.get(
    "/characters/{character_id}/spells",
    response_model=list[CharacterKnownSpellOut],
)
def list_character_spells(
    character_id: int,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    results: list[CharacterKnownSpellOut] = []

    for spell_index in character.spell_indices or []:
        try:
            spell = SpellDatasetService.get_spell(spell_index)
        except Exception:
            continue

        desc = spell.get("desc") or []
        brief_description = desc[0] if isinstance(desc, list) and desc else None

        results.append(
            CharacterKnownSpellOut(
                spell_index=spell["index"],
                spell_name_snapshot=spell["name"],
                spell_level=spell["level"],
                brief_description=brief_description,
            )
        )

    results.sort(key=lambda s: (s.spell_level, s.spell_name_snapshot.lower()))
    return results


@router.post(
    "/characters/{character_id}/spells",
    response_model=list[CharacterKnownSpellOut],
    status_code=status.HTTP_201_CREATED,
)
def add_character_spell(
    character_id: int,
    payload: CharacterSpellCreate,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    try:
        spell = SpellDatasetService.get_spell(payload.spell_index)
    except Exception:
        raise HTTPException(status_code=404, detail="Spell not found")

    if not spell_allowed_for_class(spell, character.class_name):
        raise HTTPException(
            status_code=400,
            detail=f"{character.class_name or 'This character class'} cannot learn this spell",
        )
    if not spell_allowed_for_class(spell, character.class_name):
        raise HTTPException(
            status_code=400,
            detail=f"{character.class_name or 'This character class'} cannot learn this spell",
        )

    spell_level = spell.get("level")
    if spell_level is None:
        raise HTTPException(status_code=400, detail="Spell level missing from dataset")

    if not character_has_slot_for_spell_level(character, spell_level):
        raise HTTPException(
            status_code=400,
            detail=f"Character does not have a spell slot for level {spell_level}",
        )

    current = list(character.spell_indices or [])

    if payload.spell_index in current:
        raise HTTPException(status_code=400, detail="Character already knows this spell")

    if payload.spell_index in current:
        raise HTTPException(status_code=400, detail="Character already knows this spell")

    current.append(payload.spell_index)
    character.spell_indices = current
    db.commit()
    db.refresh(character)

    return list_character_spells(character_id, db)


@router.delete(
    "/characters/{character_id}/spells/{spell_index}",
    response_model=list[CharacterKnownSpellOut],
)
def delete_character_spell(
    character_id: int,
    spell_index: str,
    db: DbSession = Depends(get_db),
):
    character = character_repo.get(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    current = list(character.spell_indices or [])

    if spell_index not in current:
        raise HTTPException(status_code=404, detail="Character does not know this spell")

    current.remove(spell_index)
    character.spell_indices = current
    db.commit()
    db.refresh(character)

    return list_character_spells(character_id, db)