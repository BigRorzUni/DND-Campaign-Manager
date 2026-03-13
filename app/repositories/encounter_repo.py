from sqlalchemy.orm import Session as DbSession

from app.models.encounter import Encounter


class EncounterRepo:
    def create(self, db: DbSession, **fields) -> Encounter:
        obj = Encounter(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, encounter_id: int) -> Encounter | None:
        return db.get(Encounter, encounter_id)

    def list_for_session(self, db: DbSession, session_id: int) -> list[Encounter]:
        return (
            db.query(Encounter)
            .filter(Encounter.session_id == session_id)
            .order_by(Encounter.id.desc())
            .all()
        )

    def update(self, db: DbSession, obj: Encounter, **fields) -> Encounter:
        for key, value in fields.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Encounter) -> None:
        db.delete(obj)
        db.commit()