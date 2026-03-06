from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.repositories.campaign_repo import CampaignRepo
from app.repositories.session_repo import SessionRepo
from app.schemas.session import SessionCreate, SessionOut, SessionUpdate

router = APIRouter(tags=["sessions"])
campaign_repo = CampaignRepo()
session_repo = SessionRepo()

@router.post(
    "/campaigns/{campaign_id}/sessions",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED
)
def create_session(campaign_id: int, payload: SessionCreate, db: DbSession = Depends(get_db)):
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return session_repo.create(
        db,
        campaign_id=campaign_id,
        date=payload.date,
        title=payload.title,
        notes=payload.notes,
        duration_minutes=payload.duration_minutes
    )

@router.get("/campaigns/{campaign_id}/sessions", response_model=list[SessionOut])
def list_sessions(campaign_id: int, db: DbSession = Depends(get_db)):
    campaign = campaign_repo.get(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return session_repo.list_for_campaign(db, campaign_id)

@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: DbSession = Depends(get_db)):
    obj = session_repo.get(db, session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Session not found")
    return obj

@router.put("/sessions/{session_id}", response_model=SessionOut)
def update_session(session_id: int, payload: SessionUpdate, db: DbSession = Depends(get_db)):
    obj = session_repo.get(db, session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_repo.update(
        db,
        obj,
        date=payload.date,
        title=payload.title,
        notes=payload.notes,
        duration_minutes=payload.duration_minutes
    )

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: DbSession = Depends(get_db)):
    obj = session_repo.get(db, session_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Session not found")
    session_repo.delete(db, obj)