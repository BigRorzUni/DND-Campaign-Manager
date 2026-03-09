from pydantic import BaseModel, Field


class CharacterResourceStateCreate(BaseModel):
    current_hp: int | None = Field(default=None, ge=0)

    spell_slots_1_current: int | None = Field(default=None, ge=0)
    spell_slots_1_max: int | None = Field(default=None, ge=0)

    spell_slots_2_current: int | None = Field(default=None, ge=0)
    spell_slots_2_max: int | None = Field(default=None, ge=0)

    spell_slots_3_current: int | None = Field(default=None, ge=0)
    spell_slots_3_max: int | None = Field(default=None, ge=0)

    hit_dice_current: int | None = Field(default=None, ge=0)
    hit_dice_max: int | None = Field(default=None, ge=0)


class CharacterResourceStateUpdate(BaseModel):
    current_hp: int | None = Field(default=None, ge=0)

    spell_slots_1_current: int | None = Field(default=None, ge=0)
    spell_slots_1_max: int | None = Field(default=None, ge=0)

    spell_slots_2_current: int | None = Field(default=None, ge=0)
    spell_slots_2_max: int | None = Field(default=None, ge=0)

    spell_slots_3_current: int | None = Field(default=None, ge=0)
    spell_slots_3_max: int | None = Field(default=None, ge=0)

    hit_dice_current: int | None = Field(default=None, ge=0)
    hit_dice_max: int | None = Field(default=None, ge=0)


class CharacterResourceStateOut(BaseModel):
    id: int
    character_id: int
    current_hp: int | None

    spell_slots_1_current: int | None
    spell_slots_1_max: int | None

    spell_slots_2_current: int | None
    spell_slots_2_max: int | None

    spell_slots_3_current: int | None
    spell_slots_3_max: int | None

    hit_dice_current: int | None
    hit_dice_max: int | None

    model_config = {"from_attributes": True}