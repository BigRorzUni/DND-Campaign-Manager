from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_db
from app.models.encounter import Encounter
from app.models.event import Event
from app.schemas.review import EncounterReviewOut

router = APIRouter(tags=["reviews"])


def classify_observed_difficulty(
    *, total_damage: int, downs: int, rounds: int | None, heals: int
) -> str:
    rounds = rounds or 0

    # simple heuristic for MVP
    if downs >= 2:
        return "Deadly"
    if downs >= 1:
        return "Hard"
    if total_damage >= 40 or rounds >= 6:
        return "Hard"
    if total_damage >= 20 or heals >= 2 or rounds >= 4:
        return "Medium"
    return "Easy"


@router.get("/encounters/{encounter_id}/review", response_model=EncounterReviewOut)
def get_encounter_review(encounter_id: int, db: DbSession = Depends(get_db)):
    encounter = db.get(Encounter, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    aggregates = (
        db.query(
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
            ).label("downs"),
            func.coalesce(
                func.sum(
                    case(
                        (Event.kind == "HEAL", 1),
                        else_=0
                    )
                ),
                0
            ).label("heals"),
        )
        .filter(Event.encounter_id == encounter_id)
        .one()
    )

    total_damage = int(aggregates.total_damage or 0)
    downs = int(aggregates.downs or 0)
    heals = int(aggregates.heals or 0)
    rounds = encounter.rounds

    observed = classify_observed_difficulty(
        total_damage=total_damage,
        downs=downs,
        rounds=rounds,
        heals=heals,
    )

    expected = encounter.expected_difficulty

    if expected is None:
        assessment = "No expected difficulty was set, so only an observed outcome can be reported."
    elif expected.lower() == observed.lower():
        assessment = "The encounter appears to have matched its intended difficulty."
    else:
        assessment = f"The encounter appears to have played {observed.lower()} relative to the intended {expected.lower()} difficulty."

    notes = (
        f"This review is based on recorded encounter events: "
        f"{total_damage} total damage, {downs} down events, {heals} healing events"
    )

    if rounds is not None:
        notes += f", and {rounds} rounds"
    notes += ". Party starting resources are not yet considered."

    return EncounterReviewOut(
        encounter_id=encounter.id,
        encounter_name=encounter.name,
        expected_difficulty=encounter.expected_difficulty,
        observed_outcome=observed,
        assessment=assessment,
        notes=notes,
        rounds=rounds,
        total_damage=total_damage,
        downs=downs,
        heals=heals,
    )