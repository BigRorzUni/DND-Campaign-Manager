from sqlalchemy.orm import Session as DbSession

from app.models.participant_action import ParticipantAction


class ParticipantActionRepo:
    def create(self, db: DbSession, **fields) -> ParticipantAction:
        obj = ParticipantAction(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def create_many(self, db: DbSession, rows: list[dict]) -> list[ParticipantAction]:
        objects = [ParticipantAction(**row) for row in rows]
        db.add_all(objects)
        db.commit()

        for obj in objects:
            db.refresh(obj)

        return objects

    def list_for_participant(self, db: DbSession, participant_id: int) -> list[ParticipantAction]:
        return (
            db.query(ParticipantAction)
            .filter(ParticipantAction.participant_id == participant_id)
            .order_by(ParticipantAction.id.asc())
            .all()
        )

    def get(self, db: DbSession, action_id: int) -> ParticipantAction | None:
        return db.get(ParticipantAction, action_id)

    def update(self, db: DbSession, obj: ParticipantAction, **fields) -> ParticipantAction:
        for key, value in fields.items():
            setattr(obj, key, value)

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: ParticipantAction) -> None:
        db.delete(obj)
        db.commit()

    def delete_for_participant(self, db: DbSession, participant_id: int) -> None:
        (
            db.query(ParticipantAction)
            .filter(ParticipantAction.participant_id == participant_id)
            .delete()
        )
        db.commit()