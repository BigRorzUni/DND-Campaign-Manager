from pydantic import BaseModel


class DamageLeaderboardEntry(BaseModel):
    source: str
    total_damage: int


class DamageTakenEntry(BaseModel):
    target: str
    total_damage_taken: int


class HealingReceivedEntry(BaseModel):
    target: str
    total_healing_received: int


class SpellUsageEntry(BaseModel):
    source: str
    total_spell_slots_used: int

class TimePlayedOut(BaseModel):
    total_minutes: int
    total_hours: float

class EncounterReviewOut(BaseModel):
    expected_difficulty: str | None
    party_damage_taken: int
    party_healing_received: int
    party_spell_slots_used: int
    party_zero_hp_count: int
    party_max_hp_total: int
    party_current_hp_total: int