# app/schemas/action.py
from pydantic import BaseModel


class ParticipantActionOut(BaseModel):
    action_type: str
    action_ref: str
    name: str
    description: str | None = None
    kind_hint: str | None = None
    spell_level: int | None = None
    available: bool = True