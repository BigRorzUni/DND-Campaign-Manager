from pydantic import BaseModel, Field


class CharacterSpellCreate(BaseModel):
    spell_index: str = Field(min_length=1, max_length=100)


class CharacterKnownSpellOut(BaseModel):
    spell_index: str
    spell_name_snapshot: str
    spell_level: int
    brief_description: str | None