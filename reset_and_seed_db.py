from pathlib import Path

from app.db.base import Base
from app.db.session import engine, SessionLocal

# Import models so SQLAlchemy registers them
import app.models  # noqa: F401

from app.models.campaign import Campaign
from app.models.character import Character
from app.models.session import Session
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event


DB_PATH = Path("dev.db")


def reset_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    Base.metadata.create_all(bind=engine)


def seed_database() -> None:
    db = SessionLocal()

    try:
        campaign = Campaign(
            name="Demo Campaign",
            description="Seeded campaign for local development",
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        ezra = Character(
            campaign_id=campaign.id,
            name="Ezra",
            role="PC",
            class_name="Wizard",
            level=5,
            max_hp=24,
            current_hp=24,
            armor_class=13,
            notes="Evocation specialist",
        )
        thalia = Character(
            campaign_id=campaign.id,
            name="Thalia",
            role="PC",
            class_name="Fighter",
            level=4,
            max_hp=30,
            current_hp=30,
            armor_class=17,
            notes="Frontline defender",
        )

        db.add_all([ezra, thalia])
        db.commit()
        db.refresh(ezra)
        db.refresh(thalia)

        session = Session(
            campaign_id=campaign.id,
            date="2026-03-09",
            title="Seeded Session",
            notes="Auto-generated demo session",
            duration_minutes=180,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        encounter = Encounter(
            session_id=session.id,
            name="Ogre Bridge Fight",
            expected_difficulty="Medium",
            rounds=4,
            notes="Seeded demo encounter",
            ai_review_cached=None,
            ai_review_is_stale=True,
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

        ezra_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=ezra.id,
            name=ezra.name,
            participant_type="PARTY",
            class_name=ezra.class_name,
            level=ezra.level,
            max_hp=ezra.max_hp,
            current_hp=14,
            spell_slots_1=3,
            spell_slots_2=1,
            spell_slots_3=1,
            notes="Used one level 1 slot already",
        )
        thalia_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=thalia.id,
            name=thalia.name,
            participant_type="PARTY",
            class_name=thalia.class_name,
            level=thalia.level,
            max_hp=thalia.max_hp,
            current_hp=22,
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            notes="Took heavy damage",
        )
        ogre_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=None,
            name="Ogre",
            participant_type="OTHER",
            class_name="Ogre",
            level=None,
            max_hp=59,
            current_hp=35,
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            notes="Main enemy",
        )

        db.add_all([ezra_p, thalia_p, ogre_p])
        db.commit()
        db.refresh(ezra_p)
        db.refresh(thalia_p)
        db.refresh(ogre_p)

        events = [
            Event(
                encounter_id=encounter.id,
                kind="DAMAGE",
                source_participant_id=ogre_p.id,
                target_participant_id=thalia_p.id,
                amount=8,
                spell_slots_consumed=None,
                detail="Club attack",
            ),
            Event(
                encounter_id=encounter.id,
                kind="DAMAGE",
                source_participant_id=ezra_p.id,
                target_participant_id=ogre_p.id,
                amount=14,
                spell_slots_consumed=1,
                detail="Chromatic Orb",
            ),
            Event(
                encounter_id=encounter.id,
                kind="HEAL",
                source_participant_id=ezra_p.id,
                target_participant_id=thalia_p.id,
                amount=4,
                spell_slots_consumed=0,
                detail="Potion / minor recovery",
            ),
            Event(
                encounter_id=encounter.id,
                kind="SPELL",
                source_participant_id=ezra_p.id,
                target_participant_id=ogre_p.id,
                amount=None,
                spell_slots_consumed=1,
                detail="Misty Step to reposition",
            ),
            Event(
                encounter_id=encounter.id,
                kind="DAMAGE",
                source_participant_id=ogre_p.id,
                target_participant_id=ezra_p.id,
                amount=10,
                spell_slots_consumed=None,
                detail="Thrown debris",
            ),
        ]

        db.add_all(events)
        db.commit()

        print("Database reset and seeded successfully.")
        print(f"Campaign ID: {campaign.id}")
        print(f"Session ID: {session.id}")
        print(f"Encounter ID: {encounter.id}")

    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
    seed_database()