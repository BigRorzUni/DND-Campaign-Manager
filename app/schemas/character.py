from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=50)
    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)
    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)
    armor_class: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    role: str | None = Field(default=None, max_length=50)
    class_name: str | None = Field(default=None, max_length=100)
    level: int | None = Field(default=None, ge=1)
    max_hp: int | None = Field(default=None, ge=0)
    current_hp: int | None = Field(default=None, ge=0)
    armor_class: int | None = Field(default=None, ge=0)
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
    notes: str | None

    model_config = {"from_attributes": True}