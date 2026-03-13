from pydantic import BaseModel, Field


class CharacterSpellCreate(BaseModel):
    spell_api_index: str
    is_prepared: bool = False
    notes: str | None = Field(default=None, max_length=1000)


class CharacterSpellOut(BaseModel):
    id: int
    character_id: int
    spell_id: int
    is_prepared: bool
    notes: str | None

    spell_api_index: str
    spell_name: str
    spell_level: int
    brief_description: str | None
    damage_dice: str | None
    damage_type: str | None
    attack_type: str | None

    model_config = {"from_attributes": True}