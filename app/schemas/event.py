from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=50)
    source_participant_id: int | None = None
    target_participant_id: int | None = None
    amount: int | None = Field(default=None, ge=0)

    action_type: str | None = Field(default=None, max_length=50)
    action_ref: str | None = Field(default=None, max_length=100)

    detail: str | None = Field(default=None, max_length=4000)


class EventUpdate(BaseModel):
    kind: str | None = Field(default=None, min_length=1, max_length=50)
    source_participant_id: int | None = None
    target_participant_id: int | None = None
    amount: int | None = Field(default=None, ge=0)

    action_type: str | None = Field(default=None, max_length=50)
    action_ref: str | None = Field(default=None, max_length=100)

    detail: str | None = Field(default=None, max_length=4000)


class EventOut(BaseModel):
    id: int
    encounter_id: int
    kind: str
    source_participant_id: int | None
    target_participant_id: int | None
    amount: int | None
    round_number: int | None

    action_type: str | None
    action_ref: str | None
    action_name_snapshot: str | None
    action_description_snapshot: str | None

    detail: str | None

    model_config = {"from_attributes": True}