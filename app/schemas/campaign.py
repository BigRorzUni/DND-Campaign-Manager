from pydantic import BaseModel, Field

class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class CampaignOut(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}