from fastapi import HTTPException

from app.services.spell_dataset import SpellDatasetService
from app.services.equipment_dataset import EquipmentDatasetService
from app.services.monster_dataset import MonsterDatasetService


class ActionResolutionService:
    @staticmethod
    def resolve_action_snapshot(
        *,
        action_type: str | None,
        action_ref: str | None,
        source_monster_index: str | None = None,
    ) -> tuple[str | None, str | None]:
        if not action_type or not action_ref:
            return None, None

        if action_type == "spell":
            try:
                spell = SpellDatasetService.get_spell(action_ref)
            except Exception:
                raise HTTPException(status_code=404, detail="Spell not found in dataset")

            desc = spell.get("desc") or []
            brief = desc[0] if isinstance(desc, list) and desc else None
            return spell.get("name"), brief

        if action_type == "equipment":
            try:
                item = EquipmentDatasetService.get_equipment(action_ref)
            except Exception:
                raise HTTPException(status_code=404, detail="Equipment not found in dataset")

            summary = EquipmentDatasetService.to_summary(item)
            description = summary.get("brief_description")
            if not description and summary.get("damage_dice"):
                description = f"{summary['damage_dice']} {summary.get('damage_type') or ''}".strip()

            return summary["name"], description

        if action_type in {"monster_action", "monster_special"}:
            if not source_monster_index:
                raise HTTPException(status_code=400, detail="Monster source required")

            monster = MonsterDatasetService.get_monster(source_monster_index)
            if not monster:
                raise HTTPException(status_code=404, detail="Monster not found")

            parts = action_ref.split("::")
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail="Invalid monster action reference")

            _, category, idx_text = parts
            idx = int(idx_text)

            if category == "action":
                actions = monster.get("actions", [])
            elif category == "special":
                actions = monster.get("special_abilities", [])
            else:
                raise HTTPException(status_code=400, detail="Invalid monster action category")

            if idx < 0 or idx >= len(actions):
                raise HTTPException(status_code=404, detail="Monster action not found")

            action = actions[idx]
            return action.get("name"), action.get("desc")

        if action_type == "custom":
            return "Custom Action", None

        raise HTTPException(status_code=400, detail="Unsupported action type")