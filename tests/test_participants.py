def test_create_linked_party_participant(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Participants Campaign", "description": "Testing participants"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Arannis",
            "role": "PC",
            "class_name": "Ranger",
            "level": 4,
            "max_hp": 32,
            "current_hp": 28,
            "armor_class": 15,
            "notes": "Archer"
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Session 1",
            "notes": "Participants test",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Easy",
            "rounds": 4,
            "notes": "Roadside ambush"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 28,
            "spell_slots_1": 2,
            "spell_slots_2": 1,
            "spell_slots_3": 0,
            "notes": "Slightly injured before combat"
        }
    )

    assert create_response.status_code == 201
    participant = create_response.json()
    assert participant["character_id"] == character["id"]
    assert participant["name"] == "Arannis"
    assert participant["class_name"] == "Ranger"
    assert participant["max_hp"] == 32
    assert participant["current_hp"] == 28


def test_create_custom_enemy_participant(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Enemy Campaign", "description": "Testing enemies"}
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Session 1",
            "notes": "Enemy test",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Easy",
            "rounds": 4,
            "notes": "Roadside ambush"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Goblin Archer",
            "participant_type": "OTHER",
            "class_name": "Goblin",
            "max_hp": 7,
            "current_hp": 7,
            "notes": "Rooftop archer"
        }
    )

    assert create_response.status_code == 201
    participant = create_response.json()
    assert participant["character_id"] is None
    assert participant["name"] == "Goblin Archer"
    assert participant["participant_type"] == "OTHER"
    assert participant["current_hp"] == 7