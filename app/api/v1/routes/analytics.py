from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession, aliased

from app.api.deps import get_db
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event
from app.models.session import Session
from app.schemas.analytics import (
    DamageLeaderboardEntry,
    DamageTakenEntry,
    HealingReceivedEntry,
    SpellUsageEntry,
    EncounterReviewOut,
    TimePlayedOut,
)
from app.services.spell_dataset import SpellDatasetService

router = APIRouter(tags=["analytics"])


def _get_spell_level_cached(
    spell_index: str,
    cache: dict[str, int | None],
) -> int | None:
    if spell_index not in cache:
        try:
            spell = SpellDatasetService.get_spell(spell_index)
            level = spell.get("level")
            cache[spell_index] = level if isinstance(level, int) else None
        except Exception:
            cache[spell_index] = None

    return cache[spell_index]


def _calculate_party_spell_slots_used_for_encounter(
    db: DbSession,
    encounter_id: int,
    party_ids: set[int],
) -> int:
    if not party_ids:
        return 0

    events = (
        db.query(Event)
        .filter(Event.encounter_id == encounter_id)
        .filter(Event.source_participant_id.in_(party_ids))
        .filter(Event.action_type == "spell")
        .all()
    )

    spell_level_cache: dict[str, int | None] = {}
    total = 0

    for event in events:
        if not event.action_ref:
            continue

        level = _get_spell_level_cached(event.action_ref, spell_level_cache)

        # Cantrips do not consume slots
        if level is not None and level > 0:
            total += 1

    return total


def _calculate_party_spell_slots_used_for_campaign(
    db: DbSession,
    campaign_id: int,
) -> dict[str, int]:
    source_participant = aliased(EncounterParticipant)

    rows = (
        db.query(
            Event,
            source_participant.name.label("source_name"),
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .join(source_participant, Event.source_participant_id == source_participant.id)
        .filter(Session.campaign_id == campaign_id)
        .filter(Encounter.is_simulated.is_(False))
        .filter(source_participant.participant_type == "PARTY")
        .filter(Event.action_type == "spell")
        .all()
    )

    spell_level_cache: dict[str, int | None] = {}
    totals_by_source: dict[str, int] = {}

    for event, source_name in rows:
        if not event.action_ref:
            continue

        level = _get_spell_level_cached(event.action_ref, spell_level_cache)
        if level is None or level == 0:
            continue

        totals_by_source[source_name] = totals_by_source.get(source_name, 0) + 1

    return totals_by_source


@router.get(
    "/campaigns/{campaign_id}/damage-leaderboard",
    response_model=list[DamageLeaderboardEntry],
)
def damage_leaderboard(campaign_id: int, db: DbSession = Depends(get_db)):
    source_participant = aliased(EncounterParticipant)

    rows = (
        db.query(
            source_participant.name.label("source"),
            func.coalesce(func.sum(Event.amount), 0).label("total_damage"),
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .join(source_participant, Event.source_participant_id == source_participant.id)
        .filter(Session.campaign_id == campaign_id)
        .filter(Encounter.is_simulated.is_(False))
        .filter(source_participant.participant_type == "PARTY")
        .filter(Event.kind == "DAMAGE")
        .group_by(source_participant.name)
        .order_by(func.coalesce(func.sum(Event.amount), 0).desc())
        .all()
    )

    return [
        DamageLeaderboardEntry(
            source=row.source,
            total_damage=row.total_damage or 0,
        )
        for row in rows
    ]


@router.get(
    "/campaigns/{campaign_id}/damage-taken",
    response_model=list[DamageTakenEntry],
)
def damage_taken(campaign_id: int, db: DbSession = Depends(get_db)):
    target_participant = aliased(EncounterParticipant)

    rows = (
        db.query(
            target_participant.name.label("target"),
            func.coalesce(func.sum(Event.amount), 0).label("total_damage_taken"),
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .join(target_participant, Event.target_participant_id == target_participant.id)
        .filter(Session.campaign_id == campaign_id)
        .filter(Encounter.is_simulated.is_(False))
        .filter(target_participant.participant_type == "PARTY")
        .filter(Event.kind == "DAMAGE")
        .group_by(target_participant.name)
        .order_by(func.coalesce(func.sum(Event.amount), 0).desc())
        .all()
    )

    return [
        DamageTakenEntry(
            target=row.target,
            total_damage_taken=row.total_damage_taken or 0,
        )
        for row in rows
    ]


@router.get(
    "/campaigns/{campaign_id}/healing-received",
    response_model=list[HealingReceivedEntry],
)
def healing_received(campaign_id: int, db: DbSession = Depends(get_db)):
    target_participant = aliased(EncounterParticipant)

    rows = (
        db.query(
            target_participant.name.label("target"),
            func.coalesce(func.sum(Event.amount), 0).label("total_healing_received"),
        )
        .join(Encounter, Event.encounter_id == Encounter.id)
        .join(Session, Encounter.session_id == Session.id)
        .join(target_participant, Event.target_participant_id == target_participant.id)
        .filter(Session.campaign_id == campaign_id)
        .filter(Encounter.is_simulated.is_(False))
        .filter(target_participant.participant_type == "PARTY")
        .filter(Event.kind == "HEAL")
        .group_by(target_participant.name)
        .order_by(func.coalesce(func.sum(Event.amount), 0).desc())
        .all()
    )

    return [
        HealingReceivedEntry(
            target=row.target,
            total_healing_received=row.total_healing_received or 0,
        )
        for row in rows
    ]


@router.get(
    "/campaigns/{campaign_id}/spell-usage",
    response_model=list[SpellUsageEntry],
)
def spell_usage(campaign_id: int, db: DbSession = Depends(get_db)):
    totals_by_source = _calculate_party_spell_slots_used_for_campaign(db, campaign_id)

    rows = [
        SpellUsageEntry(
            source=source,
            total_spell_slots_used=total,
        )
        for source, total in sorted(
            totals_by_source.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    return rows


@router.get(
    "/campaigns/{campaign_id}/time-played",
    response_model=TimePlayedOut,
)
def time_played(campaign_id: int, db: DbSession = Depends(get_db)):
    total_minutes = (
        db.query(func.coalesce(func.sum(Session.duration_minutes), 0))
        .filter(Session.campaign_id == campaign_id)
        .scalar()
        or 0
    )

    total_hours = round(total_minutes / 60.0, 2)

    return TimePlayedOut(
        total_minutes=total_minutes,
        total_hours=total_hours,
    )


@router.get(
    "/encounters/{encounter_id}/review",
    response_model=EncounterReviewOut,
)
def encounter_review(encounter_id: int, db: DbSession = Depends(get_db)):
    encounter = db.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    party_participants = (
        db.query(EncounterParticipant)
        .filter(EncounterParticipant.encounter_id == encounter_id)
        .filter(EncounterParticipant.participant_type == "PARTY")
        .all()
    )

    party_ids = [p.id for p in party_participants]
    party_id_set = set(party_ids)

    if not party_ids:
        return EncounterReviewOut(
            expected_difficulty=encounter.expected_difficulty,
            party_damage_taken=0,
            party_healing_received=0,
            party_spell_slots_used=0,
            party_zero_hp_count=0,
            party_max_hp_total=0,
            party_current_hp_total=0,
        )

    party_damage_taken = (
        db.query(func.coalesce(func.sum(Event.amount), 0))
        .filter(Event.encounter_id == encounter_id)
        .filter(Event.kind == "DAMAGE")
        .filter(Event.target_participant_id.in_(party_ids))
        .scalar()
        or 0
    )

    party_healing_received = (
        db.query(func.coalesce(func.sum(Event.amount), 0))
        .filter(Event.encounter_id == encounter_id)
        .filter(Event.kind == "HEAL")
        .filter(Event.target_participant_id.in_(party_ids))
        .scalar()
        or 0
    )

    party_spell_slots_used = _calculate_party_spell_slots_used_for_encounter(
        db,
        encounter_id,
        party_id_set,
    )

    party_zero_hp_count = sum(
        1 for p in party_participants
        if p.current_hp is not None and p.current_hp <= 0
    )

    party_max_hp_total = sum(p.max_hp or 0 for p in party_participants)
    party_current_hp_total = sum(p.current_hp or 0 for p in party_participants)

    return EncounterReviewOut(
        expected_difficulty=encounter.expected_difficulty,
        party_damage_taken=party_damage_taken,
        party_healing_received=party_healing_received,
        party_spell_slots_used=party_spell_slots_used,
        party_zero_hp_count=party_zero_hp_count,
        party_max_hp_total=party_max_hp_total,
        party_current_hp_total=party_current_hp_total,
    )