from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from app.repositories.campaign_repo import CampaignRepo

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
repo = CampaignRepo()

@router.post("", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    return repo.create(db, name=payload.name, description=payload.description)

@router.get("", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db)):
    return repo.list(db)

@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, campaign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return obj

@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(campaign_id: int, payload: CampaignUpdate, db: Session = Depends(get_db)):
    obj = repo.get(db, campaign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return repo.update(db, obj, name=payload.name, description=payload.description)

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    obj = repo.get(db, campaign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Campaign not found")
    repo.delete(db, obj)