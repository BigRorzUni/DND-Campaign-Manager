from pydantic import BaseModel, Field

class SessionCreate(BaseModel):
    date: str = Field(min_length=1, max_length=32)
    title: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)
    duration_minutes: int | None = Field(default=None, ge=0)

class SessionUpdate(BaseModel):
    date: str | None = Field(default=None, max_length=32)
    title: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=4000)
    duration_minutes: int | None = Field(default=None, ge=0)

class SessionOut(BaseModel):
    id: int
    campaign_id: int
    date: str
    title: str | None
    notes: str | None
    duration_minutes: int | None

    model_config = {"from_attributes": True}