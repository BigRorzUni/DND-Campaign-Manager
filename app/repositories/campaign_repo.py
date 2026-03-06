from sqlalchemy.orm import Session
from app.models.campaign import Campaign

class CampaignRepo:
    def create(self, db: Session, *, name: str, description: str | None) -> Campaign:
        obj = Campaign(name=name, description=description)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: Session, campaign_id: int) -> Campaign | None:
        return db.get(Campaign, campaign_id)

    def list(self, db: Session) -> list[Campaign]:
        return db.query(Campaign).order_by(Campaign.id.desc()).all()

    def update(self, db: Session, obj: Campaign, *, name: str | None, description: str | None) -> Campaign:
        if name is not None:
            obj.name = name
        if description is not None:
            obj.description = description
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: Campaign) -> None:
        db.delete(obj)
        db.commit()