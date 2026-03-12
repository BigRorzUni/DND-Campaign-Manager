from pydantic import BaseModel, Field


class EncounterParticipantCreate(BaseModel):
    character_id: int | None = None
    name: str | None = Field(default=None, max_length=200)
    participant_type: str = Field(min_length=1, max_length=50)

    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)

    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)

    spell_slots_1: int | None = Field(default=None, ge=0)
    spell_slots_2: int | None = Field(default=None, ge=0)
    spell_slots_3: int | None = Field(default=None, ge=0)
    spell_slots_4: int | None = Field(default=None, ge=0)
    spell_slots_5: int | None = Field(default=None, ge=0)
    spell_slots_6: int | None = Field(default=None, ge=0)
    spell_slots_7: int | None = Field(default=None, ge=0)
    spell_slots_8: int | None = Field(default=None, ge=0)
    spell_slots_9: int | None = Field(default=None, ge=0)

    notes: str | None = Field(default=None, max_length=1000)


class EncounterParticipantUpdate(BaseModel):
    character_id: int | None = None
    name: str | None = Field(default=None, max_length=200)
    participant_type: str | None = Field(default=None, min_length=1, max_length=50)

    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)

    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)

    spell_slots_1: int | None = Field(default=None, ge=0)
    spell_slots_2: int | None = Field(default=None, ge=0)
    spell_slots_3: int | None = Field(default=None, ge=0)
    spell_slots_4: int | None = Field(default=None, ge=0)
    spell_slots_5: int | None = Field(default=None, ge=0)
    spell_slots_6: int | None = Field(default=None, ge=0)
    spell_slots_7: int | None = Field(default=None, ge=0)
    spell_slots_8: int | None = Field(default=None, ge=0)
    spell_slots_9: int | None = Field(default=None, ge=0)

    notes: str | None = Field(default=None, max_length=1000)

class EncounterParticipantOut(BaseModel):
    id: int
    encounter_id: int
    character_id: int | None

    name: str
    participant_type: str

    class_name: str | None
    level: int | None

    max_hp: int | None
    current_hp: int | None

    spell_slots_1: int | None
    spell_slots_2: int | None
    spell_slots_3: int | None
    spell_slots_4: int | None
    spell_slots_5: int | None
    spell_slots_6: int | None
    spell_slots_7: int | None
    spell_slots_8: int | None
    spell_slots_9: int | None

    notes: str | None

    model_config = {"from_attributes": True}