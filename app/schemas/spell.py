from pydantic import BaseModel


class SpellOut(BaseModel):
    id: int
    api_index: str
    name: str
    level: int
    school: str | None
    brief_description: str | None
    range_text: str | None
    duration_text: str | None
    casting_time: str | None
    attack_type: str | None
    damage_dice: str | None
    damage_type: str | None
    dc_type: str | None
    dc_success: str | None

    model_config = {"from_attributes": True}