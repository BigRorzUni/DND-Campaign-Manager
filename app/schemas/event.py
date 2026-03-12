from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=50)
    source_participant_id: int | None = None
    target_participant_id: int | None = None
    amount: int | None = Field(default=None, ge=0)
    spell_index: str | None = Field(default=None, max_length=100)
    detail: str | None = Field(default=None, max_length=4000)


class EventUpdate(BaseModel):
    kind: str | None = Field(default=None, min_length=1, max_length=50)
    source_participant_id: int | None = None
    target_participant_id: int | None = None
    amount: int | None = Field(default=None, ge=0)
    spell_index: str | None = Field(default=None, max_length=100)
    detail: str | None = Field(default=None, max_length=4000)


class EventOut(BaseModel):
    id: int
    encounter_id: int
    kind: str
    source_participant_id: int | None
    target_participant_id: int | None
    amount: int | None
    spell_index: str | None
    spell_name_snapshot: str | None
    spell_brief_description: str | None
    spell_slots_consumed: int | None
    spell_slot_level_used: int | None
    detail: str | None

    model_config = {"from_attributes": True}