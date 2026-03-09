from sqlalchemy.orm import Session as DbSession

from app.models.encounter_participant import EncounterParticipant


class ParticipantRepo:
    def create(
        self,
        db: DbSession,
        *,
        encounter_id: int,
        character_id: int | None,
        name: str,
        participant_type: str,
        class_name: str | None,
        level: int | None,
        max_hp: int | None,
        current_hp: int | None,
        spell_slots_1: int | None,
        spell_slots_2: int | None,
        spell_slots_3: int | None,
        notes: str | None,
    ) -> EncounterParticipant:
        obj = EncounterParticipant(
            encounter_id=encounter_id,
            character_id=character_id,
            name=name,
            participant_type=participant_type,
            class_name=class_name,
            level=level,
            max_hp=max_hp,
            current_hp=current_hp,
            spell_slots_1=spell_slots_1,
            spell_slots_2=spell_slots_2,
            spell_slots_3=spell_slots_3,
            notes=notes,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_for_encounter(
        self, db: DbSession, encounter_id: int
    ) -> list[EncounterParticipant]:
        return (
            db.query(EncounterParticipant)
            .filter(EncounterParticipant.encounter_id == encounter_id)
            .order_by(EncounterParticipant.id.desc())
            .all()
        )

    def get(self, db: DbSession, participant_id: int) -> EncounterParticipant | None:
        return db.get(EncounterParticipant, participant_id)

    def delete(self, db: DbSession, obj: EncounterParticipant) -> None:
        db.delete(obj)
        db.commit()