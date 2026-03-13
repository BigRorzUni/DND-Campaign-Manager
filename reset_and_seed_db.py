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

from app.services.monster_dataset import MonsterDatasetService
from app.services.spell_dataset import SpellDatasetService
from app.services.equipment_dataset import EquipmentDatasetService
from app.services.encounter_state_service import recalculate_encounter_state
from app.services.encounter_simulation_service import EncounterSimulationService


from pathlib import Path

from app.core.config import settings


def sqlite_path_from_url(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise RuntimeError("reset_and_seed_db.py currently only supports SQLite databases.")

    raw_path = database_url[len(prefix):]
    return Path(raw_path)

def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite:///")

def reset_database() -> None:
    database_url = settings.DATABASE_URL

    if is_sqlite_url(database_url):
        db_path = sqlite_path_from_url(database_url)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        if db_path.exists():
            db_path.unlink()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_required_spell(spell_index: str) -> dict:
    spell = SpellDatasetService.get_spell(spell_index)
    if not spell:
        raise RuntimeError(
            f"Spell '{spell_index}' not found in dataset."
        )
    return spell


def get_required_equipment(equipment_index: str) -> dict:
    equipment = EquipmentDatasetService.get_equipment(equipment_index)
    if not equipment:
        raise RuntimeError(
            f"Equipment '{equipment_index}' not found in dataset."
        )
    return equipment


def get_required_monster(monster_index: str) -> dict:
    monster = MonsterDatasetService.get_monster(monster_index)
    if not monster:
        raise RuntimeError(
            f"Monster '{monster_index}' not found in dataset."
        )
    return monster


def first_desc(value: dict) -> str | None:
    desc = value.get("desc")
    if isinstance(desc, list) and desc:
        return desc[0]
    if isinstance(desc, str):
        return desc
    return None


def extract_monster_ac(monster: dict) -> int | None:
    armor_class = monster.get("armor_class")

    if isinstance(armor_class, int):
        return armor_class

    if isinstance(armor_class, list) and armor_class:
        first = armor_class[0]
        if isinstance(first, dict):
            return first.get("value")
        if isinstance(first, int):
            return first

    return None


def extract_monster_type(monster: dict) -> str | None:
    monster_type = monster.get("type")

    if isinstance(monster_type, str):
        return monster_type

    if isinstance(monster_type, dict):
        return monster_type.get("name")

    return None


def seed_database() -> None:
    db = SessionLocal()

    try:
        # ------------------------------------------------------------------
        # Campaign
        # ------------------------------------------------------------------
        campaign = Campaign(
            name="Demo Campaign",
            description="Seeded campaign for local development",
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        # ------------------------------------------------------------------
        # Resolve dataset references up front
        # ------------------------------------------------------------------
        fireball = get_required_spell("fireball")
        misty_step = get_required_spell("misty-step")
        magic_missile = get_required_spell("magic-missile")
        bane = get_required_spell("bane")

        quarterstaff = get_required_equipment("quarterstaff")
        dagger = get_required_equipment("dagger")
        shield = get_required_equipment("shield")
        longsword = get_required_equipment("longsword")

        # ------------------------------------------------------------------
        # Characters now store indices directly
        # ------------------------------------------------------------------
        ezra = Character(
            campaign_id=campaign.id,
            name="Ezra",
            role="PC",
            class_name="Wizard",
            level=5,
            max_hp=24,
            current_hp=24,
            armor_class=13,
            spell_indices=[
                fireball["index"],
                misty_step["index"],
                magic_missile["index"],
                bane["index"],
            ],
            equipment_indices=[
                quarterstaff["index"],
                dagger["index"],
            ],
            spell_slots_1=4,
            spell_slots_2=3,
            spell_slots_3=2,
            spell_slots_4=None,
            spell_slots_5=None,
            spell_slots_6=None,
            spell_slots_7=None,
            spell_slots_8=None,
            spell_slots_9=None,
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
            spell_indices=[],
            equipment_indices=[
                longsword["index"],
                shield["index"],
            ],
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            spell_slots_4=None,
            spell_slots_5=None,
            spell_slots_6=None,
            spell_slots_7=None,
            spell_slots_8=None,
            spell_slots_9=None,
            notes="Frontline defender",
        )

        db.add_all([ezra, thalia])
        db.commit()
        db.refresh(ezra)
        db.refresh(thalia)

        # ------------------------------------------------------------------
        # Session / Manual Encounter
        # ------------------------------------------------------------------
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
            notes="Seeded demo encounter",
            ai_review_cached=None,
            ai_review_is_stale=True,
            is_simulated=False,
            simulation_status=None,
            winner=None,
        )
        db.add(encounter)
        db.commit()
        db.refresh(encounter)

        # ------------------------------------------------------------------
        # Monsters come directly from dataset services
        # ------------------------------------------------------------------
        ogre = get_required_monster("ogre")
        goblin = get_required_monster("goblin")

        ogre_ac = extract_monster_ac(ogre)
        goblin_ac = extract_monster_ac(goblin)

        ogre_type = extract_monster_type(ogre)
        goblin_type = extract_monster_type(goblin)

        # ------------------------------------------------------------------
        # Manual encounter participants are snapshots of combat state
        # ------------------------------------------------------------------
        ezra_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=ezra.id,
            monster_index=None,
            name=ezra.name,
            participant_type="PARTY",
            class_name=ezra.class_name,
            level=ezra.level,
            armor_class=ezra.armor_class,
            max_hp=ezra.max_hp,
            initial_current_hp=ezra.current_hp,
            initial_spell_slots_1=ezra.spell_slots_1,
            initial_spell_slots_2=ezra.spell_slots_2,
            initial_spell_slots_3=ezra.spell_slots_3,
            initial_spell_slots_4=ezra.spell_slots_4,
            initial_spell_slots_5=ezra.spell_slots_5,
            initial_spell_slots_6=ezra.spell_slots_6,
            initial_spell_slots_7=ezra.spell_slots_7,
            initial_spell_slots_8=ezra.spell_slots_8,
            initial_spell_slots_9=ezra.spell_slots_9,
            current_hp=ezra.current_hp,
            spell_slots_1=ezra.spell_slots_1,
            spell_slots_2=ezra.spell_slots_2,
            spell_slots_3=ezra.spell_slots_3,
            spell_slots_4=ezra.spell_slots_4,
            spell_slots_5=ezra.spell_slots_5,
            spell_slots_6=ezra.spell_slots_6,
            spell_slots_7=ezra.spell_slots_7,
            spell_slots_8=ezra.spell_slots_8,
            spell_slots_9=ezra.spell_slots_9,
            notes="Wizard at encounter start",
        )

        thalia_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=thalia.id,
            monster_index=None,
            name=thalia.name,
            participant_type="PARTY",
            class_name=thalia.class_name,
            level=thalia.level,
            armor_class=thalia.armor_class,
            max_hp=thalia.max_hp,
            initial_current_hp=thalia.current_hp,
            initial_spell_slots_1=thalia.spell_slots_1,
            initial_spell_slots_2=thalia.spell_slots_2,
            initial_spell_slots_3=thalia.spell_slots_3,
            initial_spell_slots_4=thalia.spell_slots_4,
            initial_spell_slots_5=thalia.spell_slots_5,
            initial_spell_slots_6=thalia.spell_slots_6,
            initial_spell_slots_7=thalia.spell_slots_7,
            initial_spell_slots_8=thalia.spell_slots_8,
            initial_spell_slots_9=thalia.spell_slots_9,
            current_hp=thalia.current_hp,
            spell_slots_1=thalia.spell_slots_1,
            spell_slots_2=thalia.spell_slots_2,
            spell_slots_3=thalia.spell_slots_3,
            spell_slots_4=thalia.spell_slots_4,
            spell_slots_5=thalia.spell_slots_5,
            spell_slots_6=thalia.spell_slots_6,
            spell_slots_7=thalia.spell_slots_7,
            spell_slots_8=thalia.spell_slots_8,
            spell_slots_9=thalia.spell_slots_9,
            notes="Fighter at encounter start",
        )

        ogre_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=None,
            monster_index=ogre["index"],
            name=ogre["name"],
            participant_type="ENEMY",
            class_name=ogre_type,
            level=None,
            armor_class=ogre_ac,
            max_hp=ogre.get("hit_points"),
            initial_current_hp=ogre.get("hit_points"),
            initial_spell_slots_1=None,
            initial_spell_slots_2=None,
            initial_spell_slots_3=None,
            initial_spell_slots_4=None,
            initial_spell_slots_5=None,
            initial_spell_slots_6=None,
            initial_spell_slots_7=None,
            initial_spell_slots_8=None,
            initial_spell_slots_9=None,
            current_hp=ogre.get("hit_points"),
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            spell_slots_4=None,
            spell_slots_5=None,
            spell_slots_6=None,
            spell_slots_7=None,
            spell_slots_8=None,
            spell_slots_9=None,
            notes="Main enemy",
        )

        goblin_shaman_p = EncounterParticipant(
            encounter_id=encounter.id,
            character_id=None,
            monster_index=goblin["index"],
            name="Goblin Shaman",
            participant_type="ENEMY",
            class_name=goblin_type,
            level=3,
            armor_class=goblin_ac,
            max_hp=18,
            initial_current_hp=18,
            initial_spell_slots_1=2,
            initial_spell_slots_2=1,
            initial_spell_slots_3=0,
            initial_spell_slots_4=0,
            initial_spell_slots_5=0,
            initial_spell_slots_6=0,
            initial_spell_slots_7=0,
            initial_spell_slots_8=0,
            initial_spell_slots_9=0,
            current_hp=18,
            spell_slots_1=2,
            spell_slots_2=1,
            spell_slots_3=0,
            spell_slots_4=0,
            spell_slots_5=0,
            spell_slots_6=0,
            spell_slots_7=0,
            spell_slots_8=0,
            spell_slots_9=0,
            notes="Enemy support caster",
        )

        db.add_all([ezra_p, thalia_p, ogre_p, goblin_shaman_p])
        db.commit()
        db.refresh(ezra_p)
        db.refresh(thalia_p)
        db.refresh(ogre_p)
        db.refresh(goblin_shaman_p)

        # ------------------------------------------------------------------
        # Manual events use action-based fields
        # ------------------------------------------------------------------
        events = [
            Event(
                encounter_id=encounter.id,
                round_number=1,
                kind="DAMAGE",
                source_participant_id=ogre_p.id,
                target_participant_id=thalia_p.id,
                amount=8,
                action_type="monster_action",
                action_ref=f"{ogre['index']}::action::0",
                action_name_snapshot="Greatclub",
                action_description_snapshot="Club attack",
                detail="Ogre smashes Thalia with its greatclub.",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=1,
                kind="DAMAGE",
                source_participant_id=ezra_p.id,
                target_participant_id=ogre_p.id,
                amount=14,
                action_type="spell",
                action_ref=magic_missile["index"],
                action_name_snapshot=magic_missile["name"],
                action_description_snapshot=first_desc(magic_missile),
                detail="Ezra casts Magic Missile.",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=2,
                kind="HEAL",
                source_participant_id=ezra_p.id,
                target_participant_id=thalia_p.id,
                amount=4,
                action_type="custom",
                action_ref="custom",
                action_name_snapshot="Custom Action",
                action_description_snapshot=None,
                detail="Potion / minor recovery",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=2,
                kind="MISC",
                source_participant_id=ezra_p.id,
                target_participant_id=ogre_p.id,
                amount=None,
                action_type="spell",
                action_ref=misty_step["index"],
                action_name_snapshot=misty_step["name"],
                action_description_snapshot=first_desc(misty_step),
                detail="Ezra uses Misty Step to reposition.",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=3,
                kind="DAMAGE",
                source_participant_id=ogre_p.id,
                target_participant_id=ezra_p.id,
                amount=10,
                action_type="custom",
                action_ref="custom",
                action_name_snapshot="Custom Action",
                action_description_snapshot=None,
                detail="Thrown debris",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=3,
                kind="MISC",
                source_participant_id=goblin_shaman_p.id,
                target_participant_id=thalia_p.id,
                amount=None,
                action_type="spell",
                action_ref=bane["index"],
                action_name_snapshot=bane["name"],
                action_description_snapshot=first_desc(bane),
                detail="Goblin Shaman weakens the party.",
            ),
            Event(
                encounter_id=encounter.id,
                round_number=4,
                kind="DAMAGE",
                source_participant_id=goblin_shaman_p.id,
                target_participant_id=ezra_p.id,
                amount=6,
                action_type="spell",
                action_ref=magic_missile["index"],
                action_name_snapshot=magic_missile["name"],
                action_description_snapshot=first_desc(magic_missile),
                detail="Goblin Shaman casts Magic Missile.",
            ),
        ]

        db.add_all(events)
        db.commit()

        recalculate_encounter_state(db, encounter.id)

        # ------------------------------------------------------------------
        # Simulated Encounter
        # ------------------------------------------------------------------
        simulated_encounter = Encounter(
            session_id=session.id,
            name="Simulated Goblin Ambush",
            expected_difficulty="Medium",
            notes="Automatically simulated encounter",
            ai_review_cached=None,
            ai_review_is_stale=True,
            is_simulated=True,
            simulation_status="PENDING",
            winner=None,
        )
        db.add(simulated_encounter)
        db.commit()
        db.refresh(simulated_encounter)

        ezra_sim = EncounterParticipant(
            encounter_id=simulated_encounter.id,
            character_id=ezra.id,
            monster_index=None,
            name=ezra.name,
            participant_type="PARTY",
            class_name=ezra.class_name,
            level=ezra.level,
            armor_class=ezra.armor_class,
            max_hp=ezra.max_hp,
            initial_current_hp=ezra.max_hp,
            initial_spell_slots_1=ezra.spell_slots_1,
            initial_spell_slots_2=ezra.spell_slots_2,
            initial_spell_slots_3=ezra.spell_slots_3,
            initial_spell_slots_4=ezra.spell_slots_4,
            initial_spell_slots_5=ezra.spell_slots_5,
            initial_spell_slots_6=ezra.spell_slots_6,
            initial_spell_slots_7=ezra.spell_slots_7,
            initial_spell_slots_8=ezra.spell_slots_8,
            initial_spell_slots_9=ezra.spell_slots_9,
            current_hp=ezra.max_hp,
            spell_slots_1=ezra.spell_slots_1,
            spell_slots_2=ezra.spell_slots_2,
            spell_slots_3=ezra.spell_slots_3,
            spell_slots_4=ezra.spell_slots_4,
            spell_slots_5=ezra.spell_slots_5,
            spell_slots_6=ezra.spell_slots_6,
            spell_slots_7=ezra.spell_slots_7,
            spell_slots_8=ezra.spell_slots_8,
            spell_slots_9=ezra.spell_slots_9,
            notes="Wizard at simulation start",
        )

        thalia_sim = EncounterParticipant(
            encounter_id=simulated_encounter.id,
            character_id=thalia.id,
            monster_index=None,
            name=thalia.name,
            participant_type="PARTY",
            class_name=thalia.class_name,
            level=thalia.level,
            armor_class=thalia.armor_class,
            max_hp=thalia.max_hp,
            initial_current_hp=thalia.max_hp,
            initial_spell_slots_1=thalia.spell_slots_1,
            initial_spell_slots_2=thalia.spell_slots_2,
            initial_spell_slots_3=thalia.spell_slots_3,
            initial_spell_slots_4=thalia.spell_slots_4,
            initial_spell_slots_5=thalia.spell_slots_5,
            initial_spell_slots_6=thalia.spell_slots_6,
            initial_spell_slots_7=thalia.spell_slots_7,
            initial_spell_slots_8=thalia.spell_slots_8,
            initial_spell_slots_9=thalia.spell_slots_9,
            current_hp=thalia.max_hp,
            spell_slots_1=thalia.spell_slots_1,
            spell_slots_2=thalia.spell_slots_2,
            spell_slots_3=thalia.spell_slots_3,
            spell_slots_4=thalia.spell_slots_4,
            spell_slots_5=thalia.spell_slots_5,
            spell_slots_6=thalia.spell_slots_6,
            spell_slots_7=thalia.spell_slots_7,
            spell_slots_8=thalia.spell_slots_8,
            spell_slots_9=thalia.spell_slots_9,
            notes="Fighter at simulation start",
        )

        goblin_sim_1 = EncounterParticipant(
            encounter_id=simulated_encounter.id,
            character_id=None,
            monster_index=goblin["index"],
            name="Goblin Scout A",
            participant_type="ENEMY",
            class_name=goblin_type,
            level=None,
            armor_class=goblin_ac,
            max_hp=goblin.get("hit_points"),
            initial_current_hp=goblin.get("hit_points"),
            initial_spell_slots_1=None,
            initial_spell_slots_2=None,
            initial_spell_slots_3=None,
            initial_spell_slots_4=None,
            initial_spell_slots_5=None,
            initial_spell_slots_6=None,
            initial_spell_slots_7=None,
            initial_spell_slots_8=None,
            initial_spell_slots_9=None,
            current_hp=goblin.get("hit_points"),
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            spell_slots_4=None,
            spell_slots_5=None,
            spell_slots_6=None,
            spell_slots_7=None,
            spell_slots_8=None,
            spell_slots_9=None,
            notes="Simulated goblin",
        )

        goblin_sim_2 = EncounterParticipant(
            encounter_id=simulated_encounter.id,
            character_id=None,
            monster_index=goblin["index"],
            name="Goblin Scout B",
            participant_type="ENEMY",
            class_name=goblin_type,
            level=None,
            armor_class=goblin_ac,
            max_hp=goblin.get("hit_points"),
            initial_current_hp=goblin.get("hit_points"),
            initial_spell_slots_1=None,
            initial_spell_slots_2=None,
            initial_spell_slots_3=None,
            initial_spell_slots_4=None,
            initial_spell_slots_5=None,
            initial_spell_slots_6=None,
            initial_spell_slots_7=None,
            initial_spell_slots_8=None,
            initial_spell_slots_9=None,
            current_hp=goblin.get("hit_points"),
            spell_slots_1=None,
            spell_slots_2=None,
            spell_slots_3=None,
            spell_slots_4=None,
            spell_slots_5=None,
            spell_slots_6=None,
            spell_slots_7=None,
            spell_slots_8=None,
            spell_slots_9=None,
            notes="Simulated goblin",
        )

        db.add_all([ezra_sim, thalia_sim, goblin_sim_1, goblin_sim_2])
        db.commit()

        # Run the simulated encounter
        simulation_service = EncounterSimulationService()
        simulation_service.run_simulation(db, simulated_encounter.id)

        print("Database reset and seeded successfully.")
        print(f"Campaign ID: {campaign.id}")
        print(f"Session ID: {session.id}")
        print(f"Manual encounter ID: {encounter.id}")
        print(f"Simulated encounter ID: {simulated_encounter.id}")
        print(f"NPC caster participant ID: {goblin_shaman_p.id}")

    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
    seed_database()