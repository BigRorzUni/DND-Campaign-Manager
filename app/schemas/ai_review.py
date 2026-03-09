from pydantic import BaseModel


class EncounterAiReviewOut(BaseModel):
    observed_difficulty: str
    did_meet_intent: str
    resource_pressure: str
    reasoning: str
    dm_advice: str
    encounter_balance_suggestions: list[str]