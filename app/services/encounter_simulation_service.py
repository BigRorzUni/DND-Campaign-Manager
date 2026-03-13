from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session as DbSession

from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event
from app.services.ai_review_service import AiReviewService
from app.services.encounter_state_service import recalculate_encounter_state


@dataclass
class SimAction:
    action_type: str
    action_ref: str
    name: str
    description: str | None
    kind_hint: str  # DAMAGE / HEAL / MISC / CUSTOM
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

        # Remove old simulated events if re-running
        (
            db.query(Event)
            .filter(Event.encounter_id == encounter_id)
            .delete()
        )
        db.commit()

        # Reset participants to baseline state
        self._reset_participants_to_initial_state(participants)

        encounter.rounds = 0
        encounter.winner = None
        encounter.simulation_status = "RUNNING"
        db.commit()

        # Roll initiative once for the encounter
        initiative_order = self._build_initiative_order(participants)

        round_number = 0

        while round_number < self.max_rounds:
            if not self._party_alive(participants):
                encounter.winner = "ENEMY"
                break

            if not self._enemies_alive(participants):
                encounter.winner = "PARTY"
                break

            round_number += 1

            for actor in initiative_order:
                # Actor may have died earlier this round
                if not self._is_alive(actor):
                    continue

                allies = self._get_allies(participants, actor)
                enemies = self._get_enemies(participants, actor)

                if not enemies:
                    encounter.winner = "PARTY" if actor.participant_type == "PARTY" else "ENEMY"
                    break

                action = self._choose_action(actor, allies, enemies)
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
                    heal_target = self._choose_heal_target(allies)
                    if heal_target is None:
                        # No ally under threshold; fallback to damage if possible
                        damage_action = self._choose_best_damage_action(actor)
                        if damage_action is None:
                            self._record_misc_event(
                                db=db,
                                encounter_id=encounter.id,
                                round_number=round_number,
                                actor=actor,
                                target=None,
                                action_name=action.name,
                                detail="No valid healing target",
                            )
                            continue
                        self._resolve_damage_action(
                            db=db,
                            encounter_id=encounter.id,
                            round_number=round_number,
                            actor=actor,
                            target=self._choose_enemy_target(enemies),
                            action=damage_action,
                        )
                    else:
                        self._resolve_heal_action(
                            db=db,
                            encounter_id=encounter.id,
                            round_number=round_number,
                            actor=actor,
                            target=heal_target,
                            action=action,
                        )
                elif action.kind_hint == "DAMAGE":
                    target = self._choose_enemy_target(enemies)
                    self._resolve_damage_action(
                        db=db,
                        encounter_id=encounter.id,
                        round_number=round_number,
                        actor=actor,
                        target=target,
                        action=action,
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

                if not self._party_alive(participants):
                    encounter.winner = "ENEMY"
                    break

                if not self._enemies_alive(participants):
                    encounter.winner = "PARTY"
                    break

            if encounter.winner is not None:
                break

        if encounter.winner is None:
            encounter.winner = "DRAW"

        encounter.rounds = round_number
        encounter.simulation_status = "COMPLETED"
        db.commit()

        recalculate_encounter_state(db, encounter.id)
        self.ai_review_service.mark_encounter_review_stale(db, encounter.id)

    # ----------------------------- reset helpers -----------------------------

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

        # Highest roll acts first; id used as deterministic tie-break
        rolled.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in rolled]

    # ---------------------------- alive / teams ------------------------------

    def _is_alive(self, participant: EncounterParticipant) -> bool:
        return participant.current_hp is not None and participant.current_hp > 0

    def _party_alive(self, participants: list[EncounterParticipant]) -> bool:
        return any(self._is_alive(p) for p in participants if p.participant_type == "PARTY")

    def _enemies_alive(self, participants: list[EncounterParticipant]) -> bool:
        return any(self._is_alive(p) for p in participants if p.participant_type != "PARTY")

    def _get_allies(
        self,
        participants: list[EncounterParticipant],
        actor: EncounterParticipant,
    ) -> list[EncounterParticipant]:
        return [
            p for p in participants
            if p.participant_type == actor.participant_type and self._is_alive(p)
        ]

    def _get_enemies(
        self,
        participants: list[EncounterParticipant],
        actor: EncounterParticipant,
    ) -> list[EncounterParticipant]:
        return [
            p for p in participants
            if p.participant_type != actor.participant_type and self._is_alive(p)
        ]

    # ---------------------------- action selection ---------------------------

    def _choose_action(
        self,
        actor: EncounterParticipant,
        allies: list[EncounterParticipant],
        enemies: list[EncounterParticipant],
    ) -> SimAction | None:
        actions = self._build_actions_for_participant(actor)

        if not actions:
            return None

        heal_needed = any(self._below_heal_threshold(a) for a in allies)
        if heal_needed:
            healing_actions = [a for a in actions if a.kind_hint == "HEAL"]
            if healing_actions:
                return max(healing_actions, key=self._estimated_heal)

        damage_actions = [a for a in actions if a.kind_hint == "DAMAGE"]
        if damage_actions:
            return max(damage_actions, key=self._estimated_damage)

        misc_actions = [a for a in actions if a.kind_hint == "MISC"]
        return misc_actions[0] if misc_actions else None

    def _choose_best_damage_action(self, actor: EncounterParticipant) -> SimAction | None:
        actions = self._build_actions_for_participant(actor)
        damage_actions = [a for a in actions if a.kind_hint == "DAMAGE"]
        if not damage_actions:
            return None
        return max(damage_actions, key=self._estimated_damage)

    def _choose_enemy_target(
        self,
        enemies: list[EncounterParticipant],
    ) -> EncounterParticipant:
        return max(enemies, key=lambda e: e.current_hp or 0)

    def _choose_heal_target(
        self,
        allies: list[EncounterParticipant],
    ) -> EncounterParticipant | None:
        candidates = [a for a in allies if self._below_heal_threshold(a)]
        if not candidates:
            return None
        return min(candidates, key=lambda a: (a.current_hp or 0) / max(a.max_hp or 1, 1))

    def _below_heal_threshold(self, participant: EncounterParticipant) -> bool:
        if participant.current_hp is None or participant.max_hp is None or participant.max_hp <= 0:
            return False
        return (participant.current_hp / participant.max_hp) <= self.heal_threshold_ratio

    # ------------------------------ resolution ------------------------------

    def _resolve_damage_action(
        self,
        db: DbSession,
        encounter_id: int,
        round_number: int,
        actor: EncounterParticipant,
        target: EncounterParticipant,
        action: SimAction,
    ) -> None:
        attack_roll = random.randint(1, 20)
        total_to_hit = attack_roll + (action.attack_bonus or 0)
        target_ac = target.armor_class or 10

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
        if target.current_hp is not None:
            target.current_hp = max(0, target.current_hp - damage)

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
    ) -> None:
        heal_amount = self._roll_heal_for_action(action)

        if target.current_hp is not None:
            if target.max_hp is not None:
                target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
            else:
                target.current_hp += heal_amount

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
        """
        Supports simple forms like:
        1d8
        2d6+3
        4d4+4
        1d10-1
        """
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
        actor: EncounterParticipant,
    ) -> list[SimAction]:
        """
        Replace this with your real shared participant action builder.

        Expected output:
        - weapons
        - monster attacks
        - spells the actor can actually cast
        - healing actions where appropriate

        For now this method is intentionally isolated so Task 1 can focus on
        wiring the simulator into the data model before perfecting action logic.
        """
        actions: list[SimAction] = []

        # Very small fallback so simulator can run even before full action wiring:
        # if participant has a monster index, use a generic attack if no better data exists
        # if participant is a party member, you should replace this with real spell/equipment lookup

        # Placeholder basic attack:
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