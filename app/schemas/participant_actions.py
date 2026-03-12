from pydantic import BaseModel, Field


class ParticipantActionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    action_type: str = Field(default="ACTION", max_length=50)

    description: str | None = Field(default=None, max_length=4000)

    attack_bonus: int | None = None
    average_damage: int | None = Field(default=None, ge=0)
    damage_dice: str | None = Field(default=None, max_length=100)
    damage_type: str | None = Field(default=None, max_length=100)
    range_text: str | None = Field(default=None, max_length=200)

    notes: str | None = Field(default=None, max_length=1000)


class ParticipantActionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    action_type: str | None = Field(default=None, max_length=50)

    description: str | None = Field(default=None, max_length=4000)

    attack_bonus: int | None = None
    average_damage: int | None = Field(default=None, ge=0)
    damage_dice: str | None = Field(default=None, max_length=100)
    damage_type: str | None = Field(default=None, max_length=100)
    range_text: str | None = Field(default=None, max_length=200)

    notes: str | None = Field(default=None, max_length=1000)


class ParticipantActionOut(BaseModel):
    id: int
    participant_id: int

    name: str
    action_type: str

    description: str | None

    attack_bonus: int | None
    average_damage: int | None
    damage_dice: str | None
    damage_type: str | None
    range_text: str | None

    is_dataset_imported: bool
    notes: str | None

    model_config = {"from_attributes": True}