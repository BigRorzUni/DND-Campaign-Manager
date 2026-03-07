from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    kind: str = Field(min_length=1, max_length=50)
    source: str | None = Field(default=None, max_length=200)
    target: str | None = Field(default=None, max_length=200)
    amount: int | None = None
    detail: str | None = Field(default=None, max_length=4000)


class EventUpdate(BaseModel):
    kind: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=200)
    target: str | None = Field(default=None, max_length=200)
    amount: int | None = None
    detail: str | None = Field(default=None, max_length=4000)


class EventOut(BaseModel):
    id: int
    encounter_id: int
    kind: str
    source: str | None
    target: str | None
    amount: int | None
    detail: str | None

    model_config = {"from_attributes": True}