import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.api.deps import get_db


@pytest.fixture()
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_database_url = f"sqlite:///{db_path}"

    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def campaign(client):
    response = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Test Campaign",
            "description": "Test campaign description",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def session(client, campaign):
    response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Test Session",
            "notes": "Session notes",
            "duration_minutes": 180,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def normal_encounter(client, session):
    response = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Normal Encounter",
            "expected_difficulty": "Medium",
            "notes": "Normal encounter notes",
            "is_simulated": False,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def simulated_encounter(client, session):
    response = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Sim Encounter",
            "expected_difficulty": "Medium",
            "notes": "Sim encounter notes",
            "is_simulated": True,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def wizard_character(client, campaign):
    response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Ezra",
            "role": "PC",
            "class_name": "Wizard",
            "level": 5,
            "max_hp": 24,
            "current_hp": 24,
            "armor_class": 13,
            "spell_indices": [],
            "equipment_indices": [],
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "spell_slots_4": None,
            "spell_slots_5": None,
            "spell_slots_6": None,
            "spell_slots_7": None,
            "spell_slots_8": None,
            "spell_slots_9": None,
            "notes": None,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def fighter_character(client, campaign):
    response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Thalia",
            "role": "PC",
            "class_name": "Fighter",
            "level": 4,
            "max_hp": 30,
            "current_hp": 30,
            "armor_class": 17,
            "spell_indices": [],
            "equipment_indices": [],
            "spell_slots_1": None,
            "spell_slots_2": None,
            "spell_slots_3": None,
            "spell_slots_4": None,
            "spell_slots_5": None,
            "spell_slots_6": None,
            "spell_slots_7": None,
            "spell_slots_8": None,
            "spell_slots_9": None,
            "notes": None,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def wizard_participant(client, normal_encounter, wizard_character):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/participants",
        json={
            "character_id": wizard_character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "notes": None,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def fighter_participant(client, normal_encounter, fighter_character):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/participants",
        json={
            "character_id": fighter_character["id"],
            "participant_type": "PARTY",
            "current_hp": 30,
            "spell_slots_1": None,
            "spell_slots_2": None,
            "spell_slots_3": None,
            "notes": None,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def enemy_participant(client, normal_encounter):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/participants",
        json={
            "monster_index": "goblin",
            "participant_type": "ENEMY",
        },
    )
    assert response.status_code == 201
    return response.json()