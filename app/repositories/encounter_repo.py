from sqlalchemy.orm import Session as DbSession
from app.models.encounter import Encounter

class EncounterRepo:
    def create(
        self,
        db: DbSession,
        *,
        session_id: int,
        name: str,
        expected_difficulty: str | None,
        rounds: int | None,
        notes: str | None
    ) -> Encounter:
        obj = Encounter(
            session_id=session_id,
            name=name,
            expected_difficulty=expected_difficulty,
            rounds=rounds,
            notes=notes
        )
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

    def update(
        self,
        db: DbSession,
        obj: Encounter,
        *,
        name: str | None,
        expected_difficulty: str | None,
        rounds: int | None,
        notes: str | None
    ) -> Encounter:
        if name is not None:
            obj.name = name
        if expected_difficulty is not None:
            obj.expected_difficulty = expected_difficulty
        if rounds is not None:
            obj.rounds = rounds
        if notes is not None:
            obj.notes = notes

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Encounter) -> None:
        db.delete(obj)
        db.commit()