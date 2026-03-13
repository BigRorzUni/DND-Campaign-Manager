from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=50)
    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)
    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)
    armor_class: int | None = Field(default=None, ge=0)

    spell_indices: list[str] = Field(default_factory=list)
    equipment_indices: list[str] = Field(default_factory=list)

    spell_slots_1: int | None = Field(default=None, ge=0)
    spell_slots_2: int | None = Field(default=None, ge=0)
    spell_slots_3: int | None = Field(default=None, ge=0)
    spell_slots_4: int | None = Field(default=None, ge=0)
    spell_slots_5: int | None = Field(default=None, ge=0)
    spell_slots_6: int | None = Field(default=None, ge=0)
    spell_slots_7: int | None = Field(default=None, ge=0)
    spell_slots_8: int | None = Field(default=None, ge=0)
    spell_slots_9: int | None = Field(default=None, ge=0)

    notes: str | None = Field(default=None, max_length=2000)


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    role: str | None = Field(default=None, max_length=50)
    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)
    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)
    armor_class: int | None = Field(default=None, ge=0)

    spell_indices: list[str] | None = None
    equipment_indices: list[str] | None = None

    spell_slots_1: int | None = Field(default=None, ge=0)
    spell_slots_2: int | None = Field(default=None, ge=0)
    spell_slots_3: int | None = Field(default=None, ge=0)
    spell_slots_4: int | None = Field(default=None, ge=0)
    spell_slots_5: int | None = Field(default=None, ge=0)
    spell_slots_6: int | None = Field(default=None, ge=0)
    spell_slots_7: int | None = Field(default=None, ge=0)
    spell_slots_8: int | None = Field(default=None, ge=0)
    spell_slots_9: int | None = Field(default=None, ge=0)

    notes: str | None = Field(default=None, max_length=2000)


class CharacterOut(BaseModel):
    id: int
    campaign_id: int
    name: str
    role: str
    class_name: str | None
    level: int | None
    max_hp: int | None
    current_hp: int | None
    armor_class: int | None

    spell_indices: list[str]
    equipment_indices: list[str]

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