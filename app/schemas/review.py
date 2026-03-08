from pydantic import BaseModel


class EncounterReviewOut(BaseModel):
    encounter_id: int
    encounter_name: str
    expected_difficulty: str | None
    observed_outcome: str
    assessment: str
    notes: str
    rounds: int | None
    total_damage: int
    downs: int
    heals: int