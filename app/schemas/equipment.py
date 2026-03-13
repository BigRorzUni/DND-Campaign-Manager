from pydantic import BaseModel


class EquipmentOut(BaseModel):
    id: int
    api_index: str
    name: str
    category: str | None
    weapon_category: str | None
    damage_dice: str | None
    damage_type: str | None
    range_normal: int | None
    range_long: int | None
    armor_category: str | None
    armor_class_base: int | None
    armor_dex_bonus: bool | None
    armor_max_bonus: int | None
    weight: float | None
    brief_description: str | None

    model_config = {"from_attributes": True}