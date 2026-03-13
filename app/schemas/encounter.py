from pydantic import BaseModel, Field


class EncounterCreate(BaseModel):
    name: str
    expected_difficulty: str | None = None
    notes: str | None = None
    is_simulated: bool = False


class EncounterUpdate(BaseModel):
    name: str | None = None
    expected_difficulty: str | None = None
    notes: str | None = None
    is_simulated: bool | None = None
    simulation_status: str | None = None
    winner: str | None = None


class EncounterOut(BaseModel):
    id: int
    session_id: int
    name: str
    expected_difficulty: str | None
    rounds: int | None
    notes: str | None
    is_simulated: bool
    simulation_status: str | None
    winner: str | None

    model_config = {"from_attributes": True}