from sqlalchemy.orm import Session as DbSession
from app.models.character import Character


class CharacterRepo:
    def create(self, db: DbSession, **fields) -> Character:
        obj = Character(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, character_id: int):
        return db.get(Character, character_id)

    def list_for_campaign(self, db: DbSession, campaign_id: int):
        return (
            db.query(Character)
            .filter(Character.campaign_id == campaign_id)
            .order_by(Character.id.desc())
            .all()
        )

    def update(self, db: DbSession, obj: Character, **fields) -> Character:
        for key, value in fields.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Character):
        db.delete(obj)
        db.commit()