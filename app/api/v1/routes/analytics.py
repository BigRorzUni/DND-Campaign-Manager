from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, aliased

from app.api.deps import get_db
from app.models.encounter import Encounter
from app.models.event import Event
from app.models.session import Session
from app.models.encounter_participant import EncounterParticipant
from app.schemas.analytics import DamageLeaderboardEntry

router = APIRouter(tags=["analytics"])


@router.get(
    "/campaigns/{campaign_id}/damage-leaderboard",
    response_model=list[DamageLeaderboardEntry]
)
def damage_leaderboard(campaign_id: int, db: DbSession = Depends(get_db)):
    source_participant = aliased(EncounterParticipant)

    rows = (
        db.query(
            source_participant.name.label("source"),
            func.coalesce(func.sum(Event.amount), 0).label("total_damage")
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .join(
            source_participant,
            Event.source_participant_id == source_participant.id,
            isouter=True,
        )
        .filter(Session.campaign_id == campaign_id)
        .filter(Event.kind == "DAMAGE")
        .group_by(source_participant.name)
        .order_by(func.coalesce(func.sum(Event.amount), 0).desc())
        .all()
    )

    return [
        DamageLeaderboardEntry(
            source=row.source or "Unknown",
            total_damage=row.total_damage or 0
        )
        for row in rows
    ]