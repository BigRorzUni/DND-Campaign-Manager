from pydantic import BaseModel


class ActionOptionOut(BaseModel):
    action_type: str
    action_ref: str
    name: str
    description: str | None = None

    resource_kind: str | None = None          # "spell_slot" / None
    resource_level: int | None = None         # spell level if relevant
    resource_available: bool = True

    kind_hint: str | None = None              # "damage", "heal", "utility", etc.