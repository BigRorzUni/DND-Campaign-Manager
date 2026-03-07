from fastapi import APIRouter, Depends
from sqlalchemy import func, case
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.encounter import Encounter
from app.models.event import Event
from app.schemas.analytics import (
    DamageLeaderboardEntry,
    EncounterDifficultySummary,
    EventBreakdownEntry,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/campaigns/{campaign_id}/damage-leaderboard",
    response_model=list[DamageLeaderboardEntry]
)
def damage_leaderboard(campaign_id: int, db: DbSession = Depends(get_db)):
    rows = (
        db.query(
            Event.source.label("source"),
            func.coalesce(func.sum(Event.amount), 0).label("total_damage")
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .filter(Session.campaign_id == campaign_id)
        .filter(Event.kind == "DAMAGE")
        .group_by(Event.source)
        .order_by(func.coalesce(func.sum(Event.amount), 0).desc())
        .all()
    )

    return [
        DamageLeaderboardEntry(
            source=row.source,
            total_damage=int(row.total_damage or 0)
        )
        for row in rows
    ]


@router.get(
    "/campaigns/{campaign_id}/encounter-difficulty",
    response_model=list[EncounterDifficultySummary]
)
def encounter_difficulty(campaign_id: int, db: DbSession = Depends(get_db)):
    rows = (
        db.query(
            Encounter.id.label("encounter_id"),
            Encounter.name.label("encounter_name"),
            Encounter.rounds.label("rounds"),
            func.coalesce(
                func.sum(
                    case(
                        (Event.kind == "DAMAGE", Event.amount),
                        else_=0
                    )
                ),
                0
            ).label("total_damage"),
            func.coalesce(
                func.sum(
                    case(
                        (Event.kind == "DOWN", 1),
                        else_=0
                    )
                ),
                0
            ).label("downs")
        )
        .join(Session, Encounter.session_id == Session.id)
        .outerjoin(Event, Event.encounter_id == Encounter.id)
        .filter(Session.campaign_id == campaign_id)
        .group_by(Encounter.id, Encounter.name, Encounter.rounds)
        .order_by(Encounter.id.desc())
        .all()
    )

    return [
        EncounterDifficultySummary(
            encounter_id=row.encounter_id,
            encounter_name=row.encounter_name,
            rounds=row.rounds,
            total_damage=int(row.total_damage or 0),
            downs=int(row.downs or 0),
        )
        for row in rows
    ]


@router.get(
    "/campaigns/{campaign_id}/event-breakdown",
    response_model=list[EventBreakdownEntry]
)
def event_breakdown(campaign_id: int, db: DbSession = Depends(get_db)):
    rows = (
        db.query(
            Event.kind.label("kind"),
            func.count(Event.id).label("count")
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .filter(Session.campaign_id == campaign_id)
        .group_by(Event.kind)
        .order_by(func.count(Event.id).desc())
        .all()
    )

    return [
        EventBreakdownEntry(
            kind=row.kind,
            count=int(row.count)
        )
        for row in rows
    ]