from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models.encounter_participant import EncounterParticipant
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
        source_participant_id: int | None,
        target_participant_id: int | None,
        amount: int | None,
        spell_slots_consumed: int | None,
        detail: str | None,
    ) -> Event:
        normalized_kind = kind.upper()

        self._validate_event_payload(
            normalized_kind,
            amount,
            spell_slots_consumed,
        )

        event = self.event_repo.create(
            db,
            encounter_id=encounter_id,
            kind=normalized_kind,
            source_participant_id=source_participant_id,
            target_participant_id=target_participant_id,
            amount=amount,
            spell_slots_consumed=spell_slots_consumed,
            detail=detail,
        )

        self.apply_event_side_effects(db, event)
        return event

    def _validate_event_payload(
        self,
        kind: str,
        amount: int | None,
        spell_slots_consumed: int | None,
    ) -> None:
        if kind in {"DAMAGE", "HEAL"} and amount is None:
            raise HTTPException(
                status_code=400,
                detail=f"{kind} events require an amount",
            )

        if kind == "SPELL" and amount is not None:
            raise HTTPException(
                status_code=400,
                detail="SPELL events should not include an amount; use DAMAGE or HEAL for numeric spell effects",
            )

        if kind not in {"DAMAGE", "HEAL", "SPELL", "MISC"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid event kind",
            )

        if spell_slots_consumed is not None and spell_slots_consumed < 0:
            raise HTTPException(
                status_code=400,
                detail="spell_slots_consumed cannot be negative",
            )

    def apply_event_side_effects(self, db: DbSession, event: Event) -> None:
        kind = event.kind.upper()

        if kind == "DAMAGE":
            self._apply_damage(db, event.target_participant_id, event.amount)
            self._apply_spell_cost(db, event.source_participant_id, event.spell_slots_consumed)

        elif kind == "HEAL":
            self._apply_heal(db, event.target_participant_id, event.amount)
            self._apply_spell_cost(db, event.source_participant_id, event.spell_slots_consumed)

        elif kind == "SPELL":
            self._apply_spell_cost(db, event.source_participant_id, event.spell_slots_consumed)

    def _get_participant(
        self,
        db: DbSession,
        participant_id: int | None,
    ) -> EncounterParticipant | None:
        if participant_id is None:
            return None
        return db.get(EncounterParticipant, participant_id)

    def _apply_damage(
        self,
        db: DbSession,
        target_participant_id: int | None,
        amount: int | None,
    ) -> None:
        if target_participant_id is None or amount is None:
            return

        participant = self._get_participant(db, target_participant_id)
        if participant is None or participant.current_hp is None:
            return

        participant.current_hp = max(0, participant.current_hp - amount)
        db.commit()
        db.refresh(participant)

    def _apply_heal(
        self,
        db: DbSession,
        target_participant_id: int | None,
        amount: int | None,
    ) -> None:
        if target_participant_id is None or amount is None:
            return

        participant = self._get_participant(db, target_participant_id)
        if participant is None or participant.current_hp is None:
            return

        new_hp = participant.current_hp + amount
        if participant.max_hp is not None:
            new_hp = min(new_hp, participant.max_hp)

        participant.current_hp = new_hp
        db.commit()
        db.refresh(participant)

    def _apply_spell_cost(
        self,
        db: DbSession,
        source_participant_id: int | None,
        spell_slots_consumed: int | None,
    ) -> None:
        if source_participant_id is None or spell_slots_consumed is None or spell_slots_consumed <= 0:
            return

        participant = self._get_participant(db, source_participant_id)
        if participant is None:
            return

        remaining = spell_slots_consumed

        for attr in ["spell_slots_1", "spell_slots_2", "spell_slots_3"]:
            current = getattr(participant, attr)
            if current is None or current <= 0:
                continue

            used_here = min(current, remaining)
            setattr(participant, attr, current - used_here)
            remaining -= used_here

            if remaining == 0:
                break

        db.commit()
        db.refresh(participant)