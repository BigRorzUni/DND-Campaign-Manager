from pydantic import BaseModel


class EncounterParticipantCreate(BaseModel):
    character_id: int
    starting_hp: int | None = None
    starting_hp_percent: float | None = None
    spell_slots_1_start: int | None = None
    spell_slots_2_start: int | None = None
    spell_slots_3_start: int | None = None
    hit_dice_start: int | None = None
    notes: str | None = None


class EncounterParticipantOut(BaseModel):
    id: int
    encounter_id: int
    character_id: int

    character_name: str | None = None
    character_class: str | None = None
    character_level: int | None = None

    starting_hp: int | None = None
    starting_hp_percent: float | None = None
    spell_slots_1_start: int | None = None
    spell_slots_2_start: int | None = None
    spell_slots_3_start: int | None = None
    hit_dice_start: int | None = None
    notes: str | None = None