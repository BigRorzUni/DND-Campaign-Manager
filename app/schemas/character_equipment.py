from pydantic import BaseModel, Field


class CharacterEquipmentCreate(BaseModel):
    equipment_index: str = Field(min_length=1, max_length=100)


class CharacterKnownEquipmentOut(BaseModel):
    equipment_index: str
    equipment_name_snapshot: str
    category: str | None
    weapon_category: str | None
    damage_dice: str | None
    damage_type: str | None
    armor_category: str | None
    armor_class_base: int | None
    brief_description: str | None