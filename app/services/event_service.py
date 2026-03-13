from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models.encounter import Encounter
from app.repositories.event_repo import event_repo
from app.repositories.participant_repo import ParticipantRepo
from app.schemas.event import EventCreate, EventUpdate
from app.services.action_resolution_service import ActionResolutionService
from app.services.spell_dataset import SpellDatasetService


class EventService:
    def __init__(self):
        self.participant_repo = ParticipantRepo()

    def create_event(
        self,
        db: DbSession,
        encounter_id: int,
        payload: EventCreate,
    ):
        encounter = db.get(Encounter, encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        source = None
        if payload.source_participant_id is not None:
            source = self.participant_repo.get(db, payload.source_participant_id)
            if not source or source.encounter_id != encounter_id:
                raise HTTPException(status_code=400, detail="Invalid source participant")

        target = None
        if payload.target_participant_id is not None:
            target = self.participant_repo.get(db, payload.target_participant_id)
            if not target or target.encounter_id != encounter_id:
                raise HTTPException(status_code=400, detail="Invalid target participant")

        action_name_snapshot, action_description_snapshot = (
            ActionResolutionService.resolve_action_snapshot(
                action_type=payload.action_type,
                action_ref=payload.action_ref,
                source_monster_index=getattr(source, "monster_index", None) if source else None,
            )
        )

        self._apply_event_effects(
            source=source,
            target=target,
            kind=payload.kind,
            amount=payload.amount,
            action_type=payload.action_type,
            action_ref=payload.action_ref,
        )

        return event_repo.create(
            db,
            encounter_id=encounter_id,
            kind=payload.kind,
            source_participant_id=payload.source_participant_id,
            target_participant_id=payload.target_participant_id,
            amount=payload.amount,
            action_type=payload.action_type,
            action_ref=payload.action_ref,
            action_name_snapshot=action_name_snapshot,
            action_description_snapshot=action_description_snapshot,
            detail=payload.detail,
        )

    def update_event(
        self,
        db: DbSession,
        event_id: int,
        payload: EventUpdate,
    ):
        event = event_repo.get(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        encounter_id = event.encounter_id

        kind = payload.kind if payload.kind is not None else event.kind
        source_participant_id = (
            payload.source_participant_id
            if payload.source_participant_id is not None
            else event.source_participant_id
        )
        target_participant_id = (
            payload.target_participant_id
            if payload.target_participant_id is not None
            else event.target_participant_id
        )
        amount = payload.amount if payload.amount is not None else event.amount
        action_type = payload.action_type if payload.action_type is not None else event.action_type
        action_ref = payload.action_ref if payload.action_ref is not None else event.action_ref
        detail = payload.detail if payload.detail is not None else event.detail

        source = None
        if source_participant_id is not None:
            source = self.participant_repo.get(db, source_participant_id)
            if not source or source.encounter_id != encounter_id:
                raise HTTPException(status_code=400, detail="Invalid source participant")

        target = None
        if target_participant_id is not None:
            target = self.participant_repo.get(db, target_participant_id)
            if not target or target.encounter_id != encounter_id:
                raise HTTPException(status_code=400, detail="Invalid target participant")

        action_name_snapshot, action_description_snapshot = (
            ActionResolutionService.resolve_action_snapshot(
                action_type=action_type,
                action_ref=action_ref,
                source_monster_index=getattr(source, "monster_index", None) if source else None,
            )
        )

        return event_repo.update(
            db,
            event,
            kind=kind,
            source_participant_id=source_participant_id,
            target_participant_id=target_participant_id,
            amount=amount,
            action_type=action_type,
            action_ref=action_ref,
            action_name_snapshot=action_name_snapshot,
            action_description_snapshot=action_description_snapshot,
            detail=detail,
        )

    def _apply_event_effects(
        self,
        *,
        source,
        target,
        kind: str,
        amount: int | None,
        action_type: str | None,
        action_ref: str | None,
    ) -> None:
        if kind == "DAMAGE" and target and amount is not None:
            current_hp = target.current_hp or 0
            target.current_hp = max(0, current_hp - amount)

        elif kind == "HEAL" and target and amount is not None:
            current_hp = target.current_hp or 0
            max_hp = target.max_hp or 0
            target.current_hp = min(max_hp, current_hp + amount)

        if source and action_type == "spell" and action_ref:
            try:
                spell = SpellDatasetService.get_spell(action_ref)
            except Exception:
                raise HTTPException(status_code=404, detail="Spell not found in dataset")

            level = spell.get("level")
            if level is None:
                raise HTTPException(status_code=400, detail="Spell level missing from dataset")

            if level > 0:
                field_name = f"spell_slots_{level}"
                current_slots = getattr(source, field_name, 0) or 0

                if current_slots <= 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No spell slots remaining for level {level}",
                    )

                setattr(source, field_name, current_slots - 1)