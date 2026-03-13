from app.repositories.participant_repo import ParticipantRepo
from app.repositories.character_repo import CharacterRepo
from app.schemas.participant_actions import ParticipantActionOut
from app.services.spell_dataset import SpellDatasetService
from app.services.equipment_dataset import EquipmentDatasetService
from app.services.monster_dataset import MonsterDatasetService


def classify_spell_kind(spell: dict) -> str:
    if spell.get("heal_at_slot_level"):
        return "HEAL"
    if spell.get("damage"):
        return "DAMAGE"
    return "MISC"


def classify_equipment_kind(summary: dict) -> str:
    is_weapon = bool(summary.get("weapon_category")) or (summary.get("category") or "").lower() == "weapon"
    if is_weapon:
        return "DAMAGE"
    return "MISC"


def classify_monster_action_kind(action: dict, description: str | None) -> str:
    if action.get("attack_bonus") is not None:
        return "DAMAGE"
    if description and "damage" in description.lower():
        return "DAMAGE"
    return "MISC"


class ParticipantActionService:
    def __init__(self):
        self.participant_repo = ParticipantRepo()
        self.character_repo = CharacterRepo()

    def list_actions_for_participant(self, db, participant_id: int) -> list[ParticipantActionOut]:
        participant = self.participant_repo.get(db, participant_id)
        if not participant:
            raise ValueError("Participant not found")

        actions: list[ParticipantActionOut] = []

        if participant.character_id:
            character = self.character_repo.get(db, participant.character_id)
            if not character:
                raise ValueError("Character not found")

            for spell_index in character.spell_indices or []:
                try:
                    spell = SpellDatasetService.get_spell(spell_index)
                except Exception:
                    continue

                desc = spell.get("desc") or []
                brief = desc[0] if isinstance(desc, list) and desc else None
                level = spell.get("level")
                available = True if level == 0 else (getattr(participant, f"spell_slots_{level}", 0) or 0) > 0

                actions.append(
                    ParticipantActionOut(
                        action_type="spell",
                        action_ref=spell["index"],
                        name=spell["name"],
                        description=brief,
                        kind_hint=classify_spell_kind(spell),
                        spell_level=level,
                        available=available,
                    )
                )

            for equipment_index in character.equipment_indices or []:
                try:
                    item = EquipmentDatasetService.get_equipment(equipment_index)
                except Exception:
                    continue

                summary = EquipmentDatasetService.to_summary(item)

                description = summary.get("brief_description")
                if not description and summary.get("damage_dice"):
                    description = f"{summary['damage_dice']} {summary.get('damage_type') or ''}".strip()

                actions.append(
                    ParticipantActionOut(
                        action_type="equipment",
                        action_ref=summary["api_index"],
                        name=summary["name"],
                        description=description,
                        kind_hint=classify_equipment_kind(summary),
                        spell_level=None,
                        available=True,
                    )
                )

        elif participant.monster_index:
            monster = MonsterDatasetService.get_monster(participant.monster_index)
            if monster:
                for i, action in enumerate(monster.get("actions", [])):
                    desc = action.get("desc")
                    actions.append(
                        ParticipantActionOut(
                            action_type="monster_action",
                            action_ref=f"{monster['index']}::action::{i}",
                            name=action.get("name", "Unnamed Action"),
                            description=desc,
                            kind_hint=classify_monster_action_kind(action, desc),
                            spell_level=None,
                            available=True,
                        )
                    )

                for i, action in enumerate(monster.get("special_abilities", [])):
                    desc = action.get("desc")
                    actions.append(
                        ParticipantActionOut(
                            action_type="monster_special",
                            action_ref=f"{monster['index']}::special::{i}",
                            name=action.get("name", "Unnamed Special Ability"),
                            description=desc,
                            kind_hint=classify_monster_action_kind(action, desc),
                            spell_level=None,
                            available=True,
                        )
                    )

        actions.append(
            ParticipantActionOut(
                action_type="custom",
                action_ref="custom",
                name="Custom Action",
                description="Manual action entry",
                kind_hint="CUSTOM",
                spell_level=None,
                available=True,
            )
        )

        return actions