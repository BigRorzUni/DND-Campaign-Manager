from sqlalchemy.orm import Session as DbSession

from app.models.event import Event


class EventRepo:
    def create(
        self,
        db: DbSession,
        *,
        encounter_id: int,
        kind: str,
        source_participant_id: int | None,
        target_participant_id: int | None,
        amount: int | None,
        action_type: str | None,
        action_ref: str | None,
        action_name_snapshot: str | None,
        action_description_snapshot: str | None,
        detail: str | None,
    ) -> Event:
        obj = Event(
            encounter_id=encounter_id,
            kind=kind,
            source_participant_id=source_participant_id,
            target_participant_id=target_participant_id,
            amount=amount,
            action_type=action_type,
            action_ref=action_ref,
            action_name_snapshot=action_name_snapshot,
            action_description_snapshot=action_description_snapshot,
            detail=detail,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: DbSession, obj: Event, **fields) -> Event:
        for key, value in fields.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Event) -> None:
        db.delete(obj)
        db.commit()

    def get(self, db: DbSession, event_id: int) -> Event | None:
        return db.get(Event, event_id)

    def list_for_encounter(self, db: DbSession, encounter_id: int) -> list[Event]:
        return (
            db.query(Event)
            .filter(Event.encounter_id == encounter_id)
            .order_by(Event.id.desc())
            .all()
        )


event_repo = EventRepo()