from sqlalchemy.orm import Session as DbSession
from app.models.session import Session

class SessionRepo:
    def create(
        self,
        db: DbSession,
        *,
        campaign_id: int,
        date: str,
        title: str | None,
        notes: str | None,
        duration_minutes: int | None
    ) -> Session:
        obj = Session(
            campaign_id=campaign_id,
            date=date,
            title=title,
            notes=notes,
            duration_minutes=duration_minutes
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, session_id: int) -> Session | None:
        return db.get(Session, session_id)

    def list_for_campaign(self, db: DbSession, campaign_id: int) -> list[Session]:
        return (
            db.query(Session)
            .filter(Session.campaign_id == campaign_id)
            .order_by(Session.id.desc())
            .all()
        )

    def update(
        self,
        db: DbSession,
        obj: Session,
        *,
        date: str | None,
        title: str | None,
        notes: str | None,
        duration_minutes: int | None
    ) -> Session:
        if date is not None:
            obj.date = date
        if title is not None:
            obj.title = title
        if notes is not None:
            obj.notes = notes
        if duration_minutes is not None:
            obj.duration_minutes = duration_minutes

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Session) -> None:
        db.delete(obj)
        db.commit()