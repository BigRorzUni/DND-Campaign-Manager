from sqlalchemy.orm import Session as DbSession

from app.models.character_equipment import CharacterEquipment


class CharacterEquipmentRepo:
    def create(self, db: DbSession, **fields) -> CharacterEquipment:
        obj = CharacterEquipment(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, character_equipment_id: int) -> CharacterEquipment | None:
        return db.get(CharacterEquipment, character_equipment_id)

    def list_for_character(self, db: DbSession, character_id: int) -> list[CharacterEquipment]:
        return (
            db.query(CharacterEquipment)
            .filter(CharacterEquipment.character_id == character_id)
            .order_by(CharacterEquipment.id.desc())
            .all()
        )

    def find_by_character_and_equipment(self, db: DbSession, character_id: int, equipment_id: int) -> CharacterEquipment | None:
        return (
            db.query(CharacterEquipment)
            .filter(
                CharacterEquipment.character_id == character_id,
                CharacterEquipment.equipment_id == equipment_id,
            )
            .first()
        )

    def delete(self, db: DbSession, obj: CharacterEquipment) -> None:
        db.delete(obj)
        db.commit()


CharacterEquipmentRepo = CharacterEquipmentRepo()