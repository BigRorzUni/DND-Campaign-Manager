from sqlalchemy.orm import Session as DbSession

from app.models.encounter_participant_state import EncounterParticipantState


class ParticipantRepo:
    def create(
        self,
        db: DbSession,
        *,
        encounter_id: int,
        character_id: int,
        starting_hp: int | None,
        starting_hp_percent: float | None,
        spell_slots_1_start: int | None,
        spell_slots_2_start: int | None,
        spell_slots_3_start: int | None,
        hit_dice_start: int | None,
        notes: str | None,
    ) -> EncounterParticipantState:
        obj = EncounterParticipantState(
            encounter_id=encounter_id,
            character_id=character_id,
            starting_hp=starting_hp,
            starting_hp_percent=starting_hp_percent,
            spell_slots_1_start=spell_slots_1_start,
            spell_slots_2_start=spell_slots_2_start,
            spell_slots_3_start=spell_slots_3_start,
            hit_dice_start=hit_dice_start,
            notes=notes,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_encounter(
        self, db: DbSession, encounter_id: int
    ) -> list[EncounterParticipantState]:
        return (
            db.query(EncounterParticipantState)
            .filter(EncounterParticipantState.encounter_id == encounter_id)
            .order_by(EncounterParticipantState.id.desc())
            .all()
        )

    def get(self, db: DbSession, participant_id: int) -> EncounterParticipantState | None:
        return db.get(EncounterParticipantState, participant_id)

    def delete(self, db: DbSession, obj: EncounterParticipantState) -> None:
        db.delete(obj)
        db.commit()