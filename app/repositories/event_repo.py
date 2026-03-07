from sqlalchemy.orm import Session as DbSession
from app.models.event import Event


class EventRepo:
    def create(
        self,
        db: DbSession,
        *,
        encounter_id: int,
        kind: str,
        source: str | None,
        target: str | None,
        amount: int | None,
        detail: str | None
    ) -> Event:
        obj = Event(
            encounter_id=encounter_id,
            kind=kind,
            source=source,
            target=target,
            amount=amount,
            detail=detail
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, event_id: int) -> Event | None:
        return db.get(Event, event_id)

    def list_for_encounter(self, db: DbSession, encounter_id: int) -> list[Event]:
        return (
            db.query(Event)
            .filter(Event.encounter_id == encounter_id)
            .order_by(Event.id.desc())
            .all()
        )

    def update(
        self,
        db: DbSession,
        obj: Event,
        *,
        kind: str | None,
        source: str | None,
        target: str | None,
        amount: int | None,
        detail: str | None
    ) -> Event:
        if kind is not None:
            obj.kind = kind
        if source is not None:
            obj.source = source
        if target is not None:
            obj.target = target
        if amount is not None:
            obj.amount = amount
        if detail is not None:
            obj.detail = detail

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Event) -> None:
        db.delete(obj)
        db.commit()