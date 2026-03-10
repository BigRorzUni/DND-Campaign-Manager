def test_encounter_participant_stores_initial_and_current_state(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Participants Campaign", "description": "Testing participants"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Ezra",
            "role": "PC",
            "class_name": "Wizard",
            "level": 5,
            "max_hp": 24,
            "current_hp": 24,
            "armor_class": 13,
            "notes": "Caster"
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-09",
            "title": "Magic Session",
            "notes": None,
            "duration_minutes": 120
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Ogre Fight",
            "expected_difficulty": "Medium",
            "rounds": 3,
            "notes": None
        }
    ).json()

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 20,
            "spell_slots_1": 4,
            "spell_slots_2": 2,
            "spell_slots_3": 1,
            "notes": None
        }
    )

    assert response.status_code == 201
    participant = response.json()

    assert participant["current_hp"] == 20
    assert participant["spell_slots_1"] == 4
    assert participant["spell_slots_2"] == 2
    assert participant["spell_slots_3"] == 1