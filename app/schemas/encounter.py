from pydantic import BaseModel, Field

class EncounterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    expected_difficulty: str | None = Field(default=None, max_length=50)
    rounds: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=4000)

class EncounterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    expected_difficulty: str | None = Field(default=None, max_length=50)
    rounds: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=4000)

class EncounterOut(BaseModel):
    id: int
    session_id: int
    name: str
    expected_difficulty: str | None
    rounds: int | None
    notes: str | None

    model_config = {"from_attributes": True}