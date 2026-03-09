from sqlalchemy.orm import Session as DbSession

from app.models.character import Character
from app.models.character_resource_state import CharacterResourceState
from app.models.event import Event
from app.repositories.event_repo import EventRepo


class EventService:
    def __init__(self) -> None:
        self.event_repo = EventRepo()

    def create_event(
        self,
        db: DbSession,
        *,
        encounter_id: int,
        kind: str,
        source: str | None,
        target: str | None,
        source_character_id: int | None,
        target_character_id: int | None,
        amount: int | None,
        slot_level_used: int | None,
        slots_consumed: int | None,
        detail: str | None,
    ) -> Event:
        event = self.event_repo.create(
            db,
            encounter_id=encounter_id,
            kind=kind,
            source=source,
            target=target,
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            amount=amount,
            slot_level_used=slot_level_used,
            slots_consumed=slots_consumed,
            detail=detail,
        )

        self.apply_event_side_effects(db, event)
        return event

    def apply_event_side_effects(self, db: DbSession, event: Event) -> None:
        kind = event.kind.upper()

        if kind == "DAMAGE":
            self._apply_damage(db, event.target_character_id, event.amount)

        elif kind == "HEAL":
            self._apply_heal(db, event.target_character_id, event.amount)

        elif kind == "DOWN":
            self._apply_down(db, event.target_character_id)

        elif kind == "SPELL":
            self._apply_spell_slot_use(
                db,
                event.source_character_id,
                event.slot_level_used,
                event.slots_consumed,
            )

    def _get_resource_state(
        self,
        db: DbSession,
        character_id: int | None,
    ) -> CharacterResourceState | None:
        if character_id is None:
            return None

        return (
            db.query(CharacterResourceState)
            .filter(CharacterResourceState.character_id == character_id)
            .first()
        )

    def _get_character(
        self,
        db: DbSession,
        character_id: int | None,
    ) -> Character | None:
        if character_id is None:
            return None
        return db.get(Character, character_id)

    def _apply_damage(
        self,
        db: DbSession,
        target_character_id: int | None,
        amount: int | None,
    ) -> None:
        if target_character_id is None or amount is None:
            return

        resource_state = self._get_resource_state(db, target_character_id)
        if resource_state is None or resource_state.current_hp is None:
            return

        resource_state.current_hp = max(0, resource_state.current_hp - amount)
        db.commit()
        db.refresh(resource_state)

    def _apply_heal(
        self,
        db: DbSession,
        target_character_id: int | None,
        amount: int | None,
    ) -> None:
        if target_character_id is None or amount is None:
            return

        resource_state = self._get_resource_state(db, target_character_id)
        character = self._get_character(db, target_character_id)

        if resource_state is None or resource_state.current_hp is None:
            return

        new_hp = resource_state.current_hp + amount

        if character is not None and character.max_hp is not None:
            new_hp = min(new_hp, character.max_hp)

        resource_state.current_hp = new_hp
        db.commit()
        db.refresh(resource_state)

    def _apply_down(
        self,
        db: DbSession,
        target_character_id: int | None,
    ) -> None:
        if target_character_id is None:
            return

        resource_state = self._get_resource_state(db, target_character_id)
        if resource_state is None:
            return

        resource_state.current_hp = 0
        db.commit()
        db.refresh(resource_state)

    def _apply_spell_slot_use(
        self,
        db: DbSession,
        source_character_id: int | None,
        slot_level_used: int | None,
        slots_consumed: int | None,
    ) -> None:
        if source_character_id is None or slot_level_used is None:
            return

        spent = slots_consumed if slots_consumed is not None else 1

        resource_state = self._get_resource_state(db, source_character_id)
        if resource_state is None:
            return

        if slot_level_used == 1 and resource_state.spell_slots_1_current is not None:
            resource_state.spell_slots_1_current = max(
                0, resource_state.spell_slots_1_current - spent
            )

        elif slot_level_used == 2 and resource_state.spell_slots_2_current is not None:
            resource_state.spell_slots_2_current = max(
                0, resource_state.spell_slots_2_current - spent
            )

        elif slot_level_used == 3 and resource_state.spell_slots_3_current is not None:
            resource_state.spell_slots_3_current = max(
                0, resource_state.spell_slots_3_current - spent
            )

        db.commit()
        db.refresh(resource_state)