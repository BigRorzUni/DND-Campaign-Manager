from sqlalchemy.orm import Session as DbSession
from app.models.encounter_participant import EncounterParticipant


class ParticipantRepo:
    @staticmethod
    def get(db: DbSession, participant_id: int):
        return db.get(EncounterParticipant, participant_id)

    @staticmethod
    def list_for_encounter(db: DbSession, encounter_id: int):
        return (
            db.query(EncounterParticipant)
            .filter(EncounterParticipant.encounter_id == encounter_id)
            .order_by(EncounterParticipant.id)
            .all()
        )

    @staticmethod
    def create(db: DbSession, **fields):
        obj = EncounterParticipant(**fields)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update(db: DbSession, participant: EncounterParticipant, **fields):
        for key, value in fields.items():
            if value is not None:
                setattr(participant, key, value)

        db.commit()
        db.refresh(participant)
        return participant

    @staticmethod
    def delete(db: DbSession, participant: EncounterParticipant):
        db.delete(participant)
        db.commit()