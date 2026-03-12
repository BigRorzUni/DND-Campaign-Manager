from sqlalchemy.orm import Session as DbSession

from app.models.character_spell import CharacterSpell


class CharacterSpellRepo:

    def create(db: DbSession, **fields) -> CharacterSpell:
        obj = CharacterSpell(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_character(db: DbSession, character_id: int):
        return (
            db.query(CharacterSpell)
            .filter(CharacterSpell.character_id == character_id)
            .order_by(CharacterSpell.spell_level, CharacterSpell.spell_name_snapshot)
            .all()
        )

    def get(db: DbSession, spell_id: int):
        return db.get(CharacterSpell, spell_id)

    def delete(db: DbSession, obj: CharacterSpell):
        db.delete(obj)
        db.commit()