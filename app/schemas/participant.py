from pydantic import BaseModel, Field


class EncounterParticipantCreate(BaseModel):
    character_id: int
    starting_hp: int | None = Field(default=None, ge=0)
    starting_hp_percent: float | None = Field(default=None, ge=0, le=100)
    spell_slots_1_start: int | None = Field(default=None, ge=0)
    spell_slots_2_start: int | None = Field(default=None, ge=0)
    spell_slots_3_start: int | None = Field(default=None, ge=0)
    hit_dice_start: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EncounterParticipantOut(BaseModel):
    id: int
    encounter_id: int
    character_id: int
    starting_hp: int | None
    starting_hp_percent: float | None
    spell_slots_1_start: int | None
    spell_slots_2_start: int | None
    spell_slots_3_start: int | None
    hit_dice_start: int | None
    notes: str | None

    model_config = {"from_attributes": True}