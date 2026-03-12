from pydantic import BaseModel, Field


class CharacterSpellCreate(BaseModel):
    spell_index: str
    notes: str | None = Field(default=None, max_length=1000)


class CharacterSpellOut(BaseModel):
    id: int
    character_id: int
    spell_index: str
    spell_name_snapshot: str
    spell_level: int
    brief_description: str | None
    notes: str | None

    model_config = {"from_attributes": True}