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
        participant = EncounterParticipant(
            encounter_id=encounter_id,
            character_id=character_id,
            name=name,
            participant_type=participant_type,
            class_name=class_name,
            level=level,
            max_hp=max_hp,

            # immutable encounter-start baseline
            initial_current_hp=current_hp,
            initial_spell_slots_1=spell_slots_1,
            initial_spell_slots_2=spell_slots_2,
            initial_spell_slots_3=spell_slots_3,

            # mutable current state
            current_hp=current_hp,
            spell_slots_1=spell_slots_1,
            spell_slots_2=spell_slots_2,
            spell_slots_3=spell_slots_3,

            notes=notes,
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant

    def get(self, db: DbSession, participant_id: int) -> EncounterParticipant | None:
        return db.get(EncounterParticipant, participant_id)

    def list_for_encounter(self, db: DbSession, encounter_id: int) -> list[EncounterParticipant]:
        return (
            db.query(EncounterParticipant)
            .filter(EncounterParticipant.encounter_id == encounter_id)
            .order_by(EncounterParticipant.id.asc())
            .all()
        )

    def update(
        self,
        db: DbSession,
        participant: EncounterParticipant,
        *,
        name: str | None = None,
        participant_type: str | None = None,
        class_name: str | None = None,
        level: int | None = None,
        max_hp: int | None = None,
        initial_current_hp: int | None = None,
        initial_spell_slots_1: int | None = None,
        initial_spell_slots_2: int | None = None,
        initial_spell_slots_3: int | None = None,
        current_hp: int | None = None,
        spell_slots_1: int | None = None,
        spell_slots_2: int | None = None,
        spell_slots_3: int | None = None,
        notes: str | None = None,
    ) -> EncounterParticipant:
        if name is not None:
            participant.name = name
        if participant_type is not None:
            participant.participant_type = participant_type
        if class_name is not None:
            participant.class_name = class_name
        if level is not None:
            participant.level = level
        if max_hp is not None:
            participant.max_hp = max_hp
        if initial_current_hp is not None:
            participant.initial_current_hp = initial_current_hp
        if initial_spell_slots_1 is not None:
            participant.initial_spell_slots_1 = initial_spell_slots_1
        if initial_spell_slots_2 is not None:
            participant.initial_spell_slots_2 = initial_spell_slots_2
        if initial_spell_slots_3 is not None:
            participant.initial_spell_slots_3 = initial_spell_slots_3
        if current_hp is not None:
            participant.current_hp = current_hp
        if spell_slots_1 is not None:
            participant.spell_slots_1 = spell_slots_1
        if spell_slots_2 is not None:
            participant.spell_slots_2 = spell_slots_2
        if spell_slots_3 is not None:
            participant.spell_slots_3 = spell_slots_3
        if notes is not None:
            participant.notes = notes

        db.commit()
        db.refresh(participant)
        return participant

    def delete(self, db: DbSession, participant: EncounterParticipant) -> None:
        db.delete(participant)
        db.commit()


participant_repo = ParticipantRepo()