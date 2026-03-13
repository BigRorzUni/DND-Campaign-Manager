from sqlalchemy.orm import Session as DbSession

from app.models.equipment import Equipment


class EquipmentRepo:
    def get_by_api_index(self, db: DbSession, api_index: str) -> Equipment | None:
        return db.query(Equipment).filter(Equipment.api_index == api_index).first()

    def list_all(self, db: DbSession) -> list[Equipment]:
        return db.query(Equipment).order_by(Equipment.name).all()

    def search(self, db: DbSession, query: str) -> list[Equipment]:
        return (
            db.query(Equipment)
            .filter(Equipment.name.ilike(f"%{query}%"))
            .order_by(Equipment.name)
            .limit(25)
            .all()
        )

    def create(self, db: DbSession, **fields) -> Equipment:
        obj = Equipment(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def upsert_by_api_index(self, db: DbSession, api_index: str, **fields) -> Equipment:
        obj = self.get_by_api_index(db, api_index)
        if obj:
            for key, value in fields.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj

        return self.create(db, api_index=api_index, **fields)


equipment_repo = EquipmentRepo()