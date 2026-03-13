from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session as DbSession

from app.models.character import Character
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event
from app.services.action_resolution_service import ActionResolutionService
from app.services.ai_review_service import AiReviewService
from app.services.encounter_state_service import recalculate_encounter_state
from app.services.equipment_dataset import EquipmentDatasetService
from app.services.monster_dataset import MonsterDatasetService
from app.services.spell_dataset import SpellDatasetService


@dataclass
class SimAction:
    action_type: str
    action_ref: str
    name: str
    description: str | None
    kind_hint: str  # DAMAGE / HEAL / MISC
    attack_bonus: int | None = None
    damage_dice: str | None = None
    average_damage: int | None = None
    heal_dice: str | None = None
    spell_level: int | None = None


class EncounterSimulationService:
    def __init__(self) -> None:
        self.ai_review_service = AiReviewService()
        self.heal_threshold_ratio = 0.35
        self.max_rounds = 50

    # --------------------------- public entrypoint ---------------------------

    def run_simulation(self, db: DbSession, encounter_id: int) -> None:
        encounter = db.get(Encounter, encounter_id)
        if not encounter:
            raise ValueError("Encounter not found")

        participants = (
            db.query(EncounterParticipant)
            .filter(EncounterParticipant.encounter_id == encounter_id)
            .all()
        )
        if not participants:
            raise ValueError("Encounter has no participants")

        self._participant_lookup = {p.id: p for p in participants}

        # Remove old simulated events if re-running
        (
            db.query(Event)
            .filter(Event.encounter_id == encounter_id)
            .delete()
        )
        db.commit()

        # Reset persisted state back to initial
        self._reset_participants_to_initial_state(participants)

        encounter.rounds = 0
        encounter.winner = None
        encounter.simulation_status = "RUNNING"
        db.commit()

        # Build lightweight in-memory state used during simulation decisions
        sim_state = self._build_runtime_state(participants)

        # Roll initiative once for the whole encounter
        initiative_order = self._build_initiative_order(participants)
        round_number = 0

        while round_number < self.max_rounds:
            if not self._party_alive_state(sim_state):
                encounter.winner = "ENEMY"
                break

            if not self._enemies_alive_state(sim_state):
                encounter.winner = "PARTY"
                break

            round_number += 1

            for actor in initiative_order:
                actor_state = sim_state[actor.id]

                if not self._is_alive_state(actor_state):
                    continue

                allies = self._get_allies_state(sim_state, actor)
                enemies = self._get_enemies_state(sim_state, actor)

                if not enemies:
                    encounter.winner = "PARTY" if actor.participant_type == "PARTY" else "ENEMY"
                    break

                action = self._choose_action(db, actor, allies, enemies, sim_state)
                if action is None:
                    self._record_misc_event(
                        db=db,
                        encounter_id=encounter.id,
                        round_number=round_number,
                        actor=actor,
                        target=None,
                        action_name="No Action",
                        detail="No usable action available",
                    )
                    continue

                if action.kind_hint == "HEAL":
                    heal_target = self._choose_heal_target_state(allies)
                    if heal_target is None:
                        damage_action = self._choose_best_damage_action(db, actor, sim_state)
                        if damage_action is None:
                            self._record_misc_event(
                                db=db,
                                encounter_id=encounter.id,
                                round_number=round_number,
                                actor=actor,
                                target=None,
                                action_name=action.name,
                                detail="No valid healing target",
                                action=action,
                            )
                            continue

                        target = self._choose_enemy_target_state(enemies)
                        self._resolve_damage_action(
                            db=db,
                            encounter_id=encounter.id,
                            round_number=round_number,
                            actor=actor,
                            target=target,
                            action=damage_action,
                            sim_state=sim_state,
                        )
                    else:
                        self._resolve_heal_action(
                            db=db,
                            encounter_id=encounter.id,
                            round_number=round_number,
                            actor=actor,
                            target=heal_target,
                            action=action,
                            sim_state=sim_state,
                        )

                elif action.kind_hint == "DAMAGE":
                    target = self._choose_enemy_target_state(enemies)
                    self._resolve_damage_action(
                        db=db,
                        encounter_id=encounter.id,
                        round_number=round_number,
                        actor=actor,
                        target=target,
                        action=action,
                        sim_state=sim_state,
                    )

                else:
                    self._record_misc_event(
                        db=db,
                        encounter_id=encounter.id,
                        round_number=round_number,
                        actor=actor,
                        target=None,
                        action_name=action.name,
                        detail=action.description or "Misc action",
                        action=action,
                    )

                if not self._party_alive_state(sim_state):
                    encounter.winner = "ENEMY"
                    break

                if not self._enemies_alive_state(sim_state):
                    encounter.winner = "PARTY"
                    break

            if encounter.winner is not None:
                break

        if encounter.winner is None:
            encounter.winner = "DRAW"

        encounter.rounds = round_number
        encounter.simulation_status = "COMPLETED"
        db.commit()

        # Rebuild persisted participant state from the generated event log
        recalculate_encounter_state(db, encounter.id)
        self.ai_review_service.mark_encounter_review_stale(db, encounter.id)

    # --------------------------- runtime state ---------------------------

    def _build_runtime_state(
        self,
        participants: list[EncounterParticipant],
    ) -> dict[int, dict[str, Any]]:
        state: dict[int, dict[str, Any]] = {}

        for p in participants:
            state[p.id] = {
                "participant_id": p.id,
                "participant_type": p.participant_type,
                "current_hp": p.initial_current_hp,
                "max_hp": p.max_hp,
                "armor_class": p.armor_class,
                "spell_slots_1": p.initial_spell_slots_1,
                "spell_slots_2": p.initial_spell_slots_2,
                "spell_slots_3": p.initial_spell_slots_3,
                "spell_slots_4": p.initial_spell_slots_4,
                "spell_slots_5": p.initial_spell_slots_5,
                "spell_slots_6": p.initial_spell_slots_6,
                "spell_slots_7": p.initial_spell_slots_7,
                "spell_slots_8": p.initial_spell_slots_8,
                "spell_slots_9": p.initial_spell_slots_9,
            }

        return state

    def _reset_participants_to_initial_state(self, participants: list[EncounterParticipant]) -> None:
        for p in participants:
            p.current_hp = p.initial_current_hp
            p.spell_slots_1 = p.initial_spell_slots_1
            p.spell_slots_2 = p.initial_spell_slots_2
            p.spell_slots_3 = p.initial_spell_slots_3
            p.spell_slots_4 = p.initial_spell_slots_4
            p.spell_slots_5 = p.initial_spell_slots_5
            p.spell_slots_6 = p.initial_spell_slots_6
            p.spell_slots_7 = p.initial_spell_slots_7
            p.spell_slots_8 = p.initial_spell_slots_8
            p.spell_slots_9 = p.initial_spell_slots_9

    # --------------------------- initiative helpers --------------------------

    def _build_initiative_order(
        self,
        participants: list[EncounterParticipant],
    ) -> list[EncounterParticipant]:
        rolled: list[tuple[int, int, EncounterParticipant]] = []

        for p in participants:
            roll = random.randint(1, 20)
            rolled.append((roll, p.id, p))

        rolled.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in rolled]

    # ---------------------------- alive / teams ------------------------------

    def _is_alive_state(self, participant_state: dict[str, Any]) -> bool:
        hp = participant_state.get("current_hp")
        return hp is not None and hp > 0

    def _party_alive_state(self, sim_state: dict[int, dict[str, Any]]) -> bool:
        return any(
            self._is_alive_state(s)
            for s in sim_state.values()
            if s["participant_type"] == "PARTY"
        )

    def _enemies_alive_state(self, sim_state: dict[int, dict[str, Any]]) -> bool:
        return any(
            self._is_alive_state(s)
            for s in sim_state.values()
            if s["participant_type"] != "PARTY"
        )

    def _get_allies_state(
        self,
        sim_state: dict[int, dict[str, Any]],
        actor: EncounterParticipant,
    ) -> list[dict[str, Any]]:
        return [
            s for s in sim_state.values()
            if s["participant_type"] == actor.participant_type and self._is_alive_state(s)
        ]

    def _get_enemies_state(
        self,
        sim_state: dict[int, dict[str, Any]],
        actor: EncounterParticipant,
    ) -> list[dict[str, Any]]:
        return [
            s for s in sim_state.values()
            if s["participant_type"] != actor.participant_type and self._is_alive_state(s)
        ]

    # ---------------------------- action selection ---------------------------

    def _choose_action(
        self,
        db: DbSession,
        actor: EncounterParticipant,
        allies: list[dict[str, Any]],
        enemies: list[dict[str, Any]],
        sim_state: dict[int, dict[str, Any]],
    ) -> SimAction | None:
        actions = self._build_actions_for_participant(db, actor, sim_state)

        if not actions:
            return None

        heal_needed = any(self._below_heal_threshold_state(a) for a in allies)
        if heal_needed:
            healing_actions = [a for a in actions if a.kind_hint == "HEAL"]
            if healing_actions:
                return max(healing_actions, key=self._estimated_heal)

        damage_actions = [a for a in actions if a.kind_hint == "DAMAGE"]
        if damage_actions:
            return max(damage_actions, key=self._estimated_damage)

        misc_actions = [a for a in actions if a.kind_hint == "MISC"]
        return misc_actions[0] if misc_actions else None

    def _choose_best_damage_action(
        self,
        db: DbSession,
        actor: EncounterParticipant,
        sim_state: dict[int, dict[str, Any]],
    ) -> SimAction | None:
        actions = self._build_actions_for_participant(db, actor, sim_state)
        damage_actions = [a for a in actions if a.kind_hint == "DAMAGE"]
        if not damage_actions:
            return None
        return max(damage_actions, key=self._estimated_damage)

    def _choose_enemy_target_state(
        self,
        enemies: list[dict[str, Any]],
    ) -> EncounterParticipant:
        target_state = max(enemies, key=lambda e: e.get("current_hp") or 0)
        return self._participant_from_state_id(target_state["participant_id"])

    def _choose_heal_target_state(
        self,
        allies: list[dict[str, Any]],
    ) -> EncounterParticipant | None:
        candidates = [a for a in allies if self._below_heal_threshold_state(a)]
        if not candidates:
            return None
        target_state = min(
            candidates,
            key=lambda a: (a.get("current_hp") or 0) / max(a.get("max_hp") or 1, 1),
        )
        return self._participant_from_state_id(target_state["participant_id"])

    def _below_heal_threshold_state(self, participant_state: dict[str, Any]) -> bool:
        current_hp = participant_state.get("current_hp")
        max_hp = participant_state.get("max_hp")
        if current_hp is None or max_hp is None or max_hp <= 0:
            return False
        return (current_hp / max_hp) <= self.heal_threshold_ratio

    def _participant_from_state_id(self, participant_id: int) -> EncounterParticipant:
        # lightweight indirection so state stays simple
        return self._participant_lookup[participant_id]

    # ------------------------------ resolution ------------------------------

    def _resolve_damage_action(
        self,
        db: DbSession,
        encounter_id: int,
        round_number: int,
        actor: EncounterParticipant,
        target: EncounterParticipant,
        action: SimAction,
        sim_state: dict[int, dict[str, Any]],
    ) -> None:
        attack_roll = random.randint(1, 20)
        total_to_hit = attack_roll + (action.attack_bonus or 0)
        target_ac = sim_state[target.id].get("armor_class") or target.armor_class or 10

        if total_to_hit < target_ac:
            self._record_misc_event(
                db=db,
                encounter_id=encounter_id,
                round_number=round_number,
                actor=actor,
                target=target,
                action_name=action.name,
                detail=f"Missed: rolled {total_to_hit} vs AC {target_ac}",
                action=action,
            )
            return

        damage = self._roll_damage_for_action(action)
        current_hp = sim_state[target.id].get("current_hp")
        if current_hp is not None:
            sim_state[target.id]["current_hp"] = max(0, current_hp - damage)

        self._consume_spell_slot_if_needed(sim_state, actor.id, action)

        event = Event(
            encounter_id=encounter_id,
            round_number=round_number,
            kind="DAMAGE",
            source_participant_id=actor.id,
            target_participant_id=target.id,
            amount=damage,
            action_type=action.action_type,
            action_ref=action.action_ref,
            action_name_snapshot=action.name,
            action_description_snapshot=action.description,
            detail=f"Hit: rolled {total_to_hit} vs AC {target_ac}",
        )
        db.add(event)
        db.commit()

    def _resolve_heal_action(
        self,
        db: DbSession,
        encounter_id: int,
        round_number: int,
        actor: EncounterParticipant,
        target: EncounterParticipant,
        action: SimAction,
        sim_state: dict[int, dict[str, Any]],
    ) -> None:
        heal_amount = self._roll_heal_for_action(action)
        current_hp = sim_state[target.id].get("current_hp")
        max_hp = sim_state[target.id].get("max_hp")

        if current_hp is not None:
            if max_hp is not None:
                sim_state[target.id]["current_hp"] = min(max_hp, current_hp + heal_amount)
            else:
                sim_state[target.id]["current_hp"] = current_hp + heal_amount

        self._consume_spell_slot_if_needed(sim_state, actor.id, action)

        event = Event(
            encounter_id=encounter_id,
            round_number=round_number,
            kind="HEAL",
            source_participant_id=actor.id,
            target_participant_id=target.id,
            amount=heal_amount,
            action_type=action.action_type,
            action_ref=action.action_ref,
            action_name_snapshot=action.name,
            action_description_snapshot=action.description,
            detail=f"Healed for {heal_amount}",
        )
        db.add(event)
        db.commit()

    def _record_misc_event(
        self,
        db: DbSession,
        encounter_id: int,
        round_number: int,
        actor: EncounterParticipant,
        target: EncounterParticipant | None,
        action_name: str,
        detail: str,
        action: SimAction | None = None,
    ) -> None:
        event = Event(
            encounter_id=encounter_id,
            round_number=round_number,
            kind="MISC",
            source_participant_id=actor.id,
            target_participant_id=target.id if target else None,
            amount=None,
            action_type=action.action_type if action else "custom",
            action_ref=action.action_ref if action else "sim-misc",
            action_name_snapshot=action.name if action else action_name,
            action_description_snapshot=action.description if action else None,
            detail=detail,
        )
        db.add(event)
        db.commit()

    # --------------------------- estimation / dice ---------------------------

    def _estimated_damage(self, action: SimAction) -> float:
        if action.average_damage is not None:
            return float(action.average_damage)
        if action.damage_dice:
            return self._average_from_dice(action.damage_dice)
        return 0.0

    def _estimated_heal(self, action: SimAction) -> float:
        if action.heal_dice:
            return self._average_from_dice(action.heal_dice)
        return 0.0

    def _roll_damage_for_action(self, action: SimAction) -> int:
        if action.damage_dice:
            return max(0, self._roll_dice(action.damage_dice))
        if action.average_damage is not None:
            return max(0, action.average_damage)
        return 0

    def _roll_heal_for_action(self, action: SimAction) -> int:
        if action.heal_dice:
            return max(0, self._roll_dice(action.heal_dice))
        return 0

    def _roll_dice(self, dice: str) -> int:
        match = re.fullmatch(r"\s*(\d+)d(\d+)([+-]\d+)?\s*", dice)
        if not match:
            return 0

        count = int(match.group(1))
        sides = int(match.group(2))
        modifier = int(match.group(3) or 0)

        total = sum(random.randint(1, sides) for _ in range(count))
        return total + modifier

    def _average_from_dice(self, dice: str) -> float:
        match = re.fullmatch(r"\s*(\d+)d(\d+)([+-]\d+)?\s*", dice)
        if not match:
            return 0.0

        count = int(match.group(1))
        sides = int(match.group(2))
        modifier = int(match.group(3) or 0)

        return count * ((1 + sides) / 2.0) + modifier

    # ---------------------------- action builder -----------------------------

    def _build_actions_for_participant(
        self,
        db: DbSession,
        actor: EncounterParticipant,
        sim_state: dict[int, dict[str, Any]],
    ) -> list[SimAction]:
        actions: list[SimAction] = []

        if actor.monster_index:
            try:
                monster = MonsterDatasetService.get_monster(actor.monster_index)
                if monster:
                    actions.extend(self._build_monster_actions(actor, monster))
            except Exception:
                pass

        if actor.character_id:
            character = db.get(Character, actor.character_id)
            if character:
                actions.extend(self._build_character_spell_actions(actor, character, sim_state))
                actions.extend(self._build_character_equipment_actions(actor, character))

        if not actions:
            actions.append(
                SimAction(
                    action_type="custom",
                    action_ref="basic-attack",
                    name="Basic Attack",
                    description="Fallback simulated attack",
                    kind_hint="DAMAGE",
                    attack_bonus=5,
                    damage_dice="1d8+2",
                    average_damage=6,
                )
            )

        return actions

    def _build_monster_actions(
        self,
        actor: EncounterParticipant,
        monster: dict[str, Any],
    ) -> list[SimAction]:
        actions: list[SimAction] = []

        for idx, raw_action in enumerate(monster.get("actions", [])):
            attack_bonus = raw_action.get("attack_bonus")
            damage_entries = raw_action.get("damage") or []

            damage_dice = None
            if damage_entries and isinstance(damage_entries[0], dict):
                damage_dice = damage_entries[0].get("damage_dice")

            if attack_bonus is None and not damage_dice:
                continue

            action_ref = f"{monster['index']}::action::{idx}"
            name, description = ActionResolutionService.resolve_action_snapshot(
                action_type="monster_action",
                action_ref=action_ref,
                source_monster_index=actor.monster_index,
            )

            actions.append(
                SimAction(
                    action_type="monster_action",
                    action_ref=action_ref,
                    name=name or raw_action.get("name") or "Monster Action",
                    description=description,
                    kind_hint="DAMAGE",
                    attack_bonus=attack_bonus or 0,
                    damage_dice=damage_dice,
                    average_damage=int(self._average_from_dice(damage_dice)) if damage_dice else None,
                )
            )

        return actions

    def _build_character_spell_actions(
        self,
        actor: EncounterParticipant,
        character: Character,
        sim_state: dict[int, dict[str, Any]],
    ) -> list[SimAction]:
        actions: list[SimAction] = []

        for spell_index in character.spell_indices or []:
            try:
                spell = SpellDatasetService.get_spell(spell_index)
            except Exception:
                continue

            if not spell:
                continue

            level = spell.get("level")
            if not isinstance(level, int):
                continue

            if level > 0 and not self._has_spell_slot(sim_state, actor.id, level):
                continue

            name, description = ActionResolutionService.resolve_action_snapshot(
                action_type="spell",
                action_ref=spell_index,
            )

            heal_dice = None
            heal_at_slot = spell.get("heal_at_slot_level")
            if isinstance(heal_at_slot, dict):
                heal_dice = heal_at_slot.get(str(level)) or next(iter(heal_at_slot.values()), None)

            if heal_dice:
                actions.append(
                    SimAction(
                        action_type="spell",
                        action_ref=spell_index,
                        name=name or spell.get("name") or spell_index,
                        description=description,
                        kind_hint="HEAL",
                        heal_dice=heal_dice,
                        spell_level=level,
                    )
                )

            damage_dice = self._extract_spell_damage_dice(spell, level)
            if damage_dice:
                actions.append(
                    SimAction(
                        action_type="spell",
                        action_ref=spell_index,
                        name=name or spell.get("name") or spell_index,
                        description=description,
                        kind_hint="DAMAGE",
                        attack_bonus=self._estimate_spell_attack_bonus(actor),
                        damage_dice=damage_dice,
                        average_damage=int(self._average_from_dice(damage_dice)),
                        spell_level=level,
                    )
                )

        return actions

    def _build_character_equipment_actions(
        self,
        actor: EncounterParticipant,
        character: Character,
    ) -> list[SimAction]:
        actions: list[SimAction] = []

        for equipment_index in character.equipment_indices or []:
            try:
                item = EquipmentDatasetService.get_equipment(equipment_index)
            except Exception:
                continue

            if not item:
                continue

            damage = item.get("damage") or {}
            damage_dice = damage.get("damage_dice")
            if not damage_dice:
                continue

            name, description = ActionResolutionService.resolve_action_snapshot(
                action_type="equipment",
                action_ref=equipment_index,
            )

            actions.append(
                SimAction(
                    action_type="equipment",
                    action_ref=equipment_index,
                    name=name or item.get("name") or equipment_index,
                    description=description,
                    kind_hint="DAMAGE",
                    attack_bonus=self._estimate_equipment_attack_bonus(actor),
                    damage_dice=damage_dice,
                    average_damage=int(self._average_from_dice(damage_dice)),
                )
            )

        return actions

    def _extract_spell_damage_dice(
        self,
        spell: dict[str, Any],
        level: int,
    ) -> str | None:
        damage = spell.get("damage") or {}

        damage_at_slot = damage.get("damage_at_slot_level")
        if isinstance(damage_at_slot, dict):
            return damage_at_slot.get(str(level)) or next(iter(damage_at_slot.values()), None)

        damage_at_level = damage.get("damage_at_character_level")
        if isinstance(damage_at_level, dict):
            return next(iter(damage_at_level.values()), None)

        return None

    def _has_spell_slot(
        self,
        sim_state: dict[int, dict[str, Any]],
        participant_id: int,
        level: int,
    ) -> bool:
        if level <= 0:
            return True
        value = sim_state[participant_id].get(f"spell_slots_{level}")
        return value is not None and value > 0

    def _consume_spell_slot_if_needed(
        self,
        sim_state: dict[int, dict[str, Any]],
        participant_id: int,
        action: SimAction,
    ) -> None:
        if action.action_type != "spell":
            return
        if action.spell_level is None or action.spell_level <= 0:
            return

        field = f"spell_slots_{action.spell_level}"
        current = sim_state[participant_id].get(field)
        current = current if current is not None else 0
        sim_state[participant_id][field] = max(0, current - 1)

    def _estimate_spell_attack_bonus(self, actor: EncounterParticipant) -> int:
        if actor.level is not None:
            return 2 + max(2, actor.level // 4)
        return 5

    def _estimate_equipment_attack_bonus(self, actor: EncounterParticipant) -> int:
        if actor.level is not None:
            return 2 + max(2, actor.level // 4)
        return 5