from pydantic import BaseModel


class DamageLeaderboardEntry(BaseModel):
    source: str | None
    total_damage: int


class EncounterDifficultySummary(BaseModel):
    encounter_id: int
    encounter_name: str
    rounds: int | None
    total_damage: int
    downs: int


class EventBreakdownEntry(BaseModel):
    kind: str
    count: int