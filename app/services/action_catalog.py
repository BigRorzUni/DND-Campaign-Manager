from app.repositories.character_repo import CharacterRepo
from app.repositories.participant_repo import ParticipantRepo
from app.schemas.action import ActionOptionOut
from app.services.spell_dataset import SpellDatasetService
from app.services.equipment_dataset import EquipmentDatasetService
from app.services.monster_dataset import MonsterDatasetService


class ActionCatalogService:
    def __init__(self):
        self.character_repo = CharacterRepo()
        self.participant_repo = ParticipantRepo()

    def list_actions_for_participant(self, db, participant_id: int) -> list[ActionOptionOut]:
        participant = self.participant_repo.get(db, participant_id)
        if not participant:
            raise ValueError("Participant not found")

        actions: list[ActionOptionOut] = []

        if participant.character_id is not None:
            character = self.character_repo.get(db, participant.character_id)
            if not character:
                raise ValueError("Character not found")

            actions.extend(self._spell_actions(character))
            actions.extend(self._equipment_actions(character))

        elif participant.monster_index is not None:
            monster = MonsterDatasetService.get_monster(participant.monster_index)
            if monster:
                actions.extend(self._monster_actions(monster))

        actions.append(
            ActionOptionOut(
                action_type="custom",
                action_ref="custom",
                name="Custom Action",
                description="Manual action entry",
                resource_available=True,
            )
        )

        return actions

    def _spell_actions(self, character) -> list[ActionOptionOut]:
        results: list[ActionOptionOut] = []

        for spell_index in character.spell_indices or []:
            try:
                spell = SpellDatasetService.get_spell(spell_index)
            except Exception:
                continue

            desc = spell.get("desc") or []
            brief = desc[0] if isinstance(desc, list) and desc else None
            level = spell.get("level")

            available = True
            if isinstance(level, int) and level > 0:
                available = self._has_spell_slot(character, level)

            results.append(
                ActionOptionOut(
                    action_type="spell",
                    action_ref=spell["index"],
                    name=spell["name"],
                    description=brief,
                    resource_kind="spell_slot" if level and level > 0 else None,
                    resource_level=level if isinstance(level, int) else None,
                    resource_available=available,
                    kind_hint=self._infer_spell_kind(spell),
                )
            )

        return results

    def _equipment_actions(self, character) -> list[ActionOptionOut]:
        results: list[ActionOptionOut] = []

        for equipment_index in character.equipment_indices or []:
            try:
                item = EquipmentDatasetService.get_equipment(equipment_index)
            except Exception:
                continue

            summary = EquipmentDatasetService.to_summary(item)
            results.append(
                ActionOptionOut(
                    action_type="equipment",
                    action_ref=summary["api_index"],
                    name=summary["name"],
                    description=summary["brief_description"],
                    resource_available=True,
                    kind_hint="damage",
                )
            )

        return results

    def _monster_actions(self, monster: dict) -> list[ActionOptionOut]:
        results: list[ActionOptionOut] = []

        for i, action in enumerate(monster.get("actions", [])):
            desc = action.get("desc")
            results.append(
                ActionOptionOut(
                    action_type="monster_action",
                    action_ref=f"{monster['index']}::action::{i}",
                    name=action.get("name", "Unnamed Action"),
                    description=desc,
                    resource_available=True,
                    kind_hint="damage",
                )
            )

        for i, action in enumerate(monster.get("special_abilities", [])):
            results.append(
                ActionOptionOut(
                    action_type="monster_special",
                    action_ref=f"{monster['index']}::special::{i}",
                    name=action.get("name", "Unnamed Special Ability"),
                    description=action.get("desc"),
                    resource_available=True,
                    kind_hint="utility",
                )
            )

        return results

    def _has_spell_slot(self, character, level: int) -> bool:
        value = getattr(character, f"spell_slots_{level}", None)
        return value is not None and value > 0

    def _infer_spell_kind(self, spell: dict) -> str | None:
        desc = " ".join(spell.get("desc", [])).lower()

        if "regain hit points" in desc or "healing" in desc:
            return "heal"
        if "damage" in desc:
            return "damage"
        return "utility"