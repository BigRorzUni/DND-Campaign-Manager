from pydantic import BaseModel, Field


class CharacterEquipmentCreate(BaseModel):
    equipment_api_index: str
    quantity: int = Field(default=1, ge=1)
    equipped: bool = False
    notes: str | None = Field(default=None, max_length=1000)


class CharacterEquipmentOut(BaseModel):
    id: int
    character_id: int
    equipment_id: int
    quantity: int
    equipped: bool
    notes: str | None

    equipment_api_index: str
    equipment_name: str
    category: str | None
    damage_dice: str | None
    damage_type: str | None
    armor_class_base: int | None
    brief_description: str | None

    model_config = {"from_attributes": True}