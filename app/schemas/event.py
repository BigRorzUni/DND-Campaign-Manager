from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=50)
    source: str | None = Field(default=None, max_length=200)
    target: str | None = Field(default=None, max_length=200)

    source_character_id: int | None = None
    target_character_id: int | None = None

    amount: int | None = None
    slot_level_used: int | None = Field(default=None, ge=1, le=9)
    slots_consumed: int | None = Field(default=1, ge=0)

    detail: str | None = Field(default=None, max_length=4000)


class EventUpdate(BaseModel):
    kind: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=200)
    target: str | None = Field(default=None, max_length=200)

    source_character_id: int | None = None
    target_character_id: int | None = None

    amount: int | None = None
    slot_level_used: int | None = Field(default=None, ge=1, le=9)
    slots_consumed: int | None = Field(default=1, ge=0)

    detail: str | None = Field(default=None, max_length=4000)


class EventOut(BaseModel):
    id: int
    encounter_id: int
    kind: str
    source: str | None
    target: str | None

    source_character_id: int | None
    target_character_id: int | None

    amount: int | None
    slot_level_used: int | None
    slots_consumed: int | None
    detail: str | None

    model_config = {"from_attributes": True}