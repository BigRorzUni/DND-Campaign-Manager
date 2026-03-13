from sqlalchemy.orm import Session as DbSession

from app.models.spell import Spell


class SpellRepo:
    def get_by_api_index(self, db: DbSession, api_index: str) -> Spell | None:
        return db.query(Spell).filter(Spell.api_index == api_index).first()

    def list_all(self, db: DbSession) -> list[Spell]:
        return db.query(Spell).order_by(Spell.level, Spell.name).all()

    def search(self, db: DbSession, query: str) -> list[Spell]:
        return (
            db.query(Spell)
            .filter(Spell.name.ilike(f"%{query}%"))
            .order_by(Spell.level, Spell.name)
            .limit(25)
            .all()
        )

    def create(self, db: DbSession, **fields) -> Spell:
        obj = Spell(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def upsert_by_api_index(self, db: DbSession, api_index: str, **fields) -> Spell:
        obj = self.get_by_api_index(db, api_index)
        if obj:
            for key, value in fields.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj

        return self.create(db, api_index=api_index, **fields)


spell_repo = SpellRepo()