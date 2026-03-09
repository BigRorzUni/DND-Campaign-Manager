def test_damage_leaderboard(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Analytics Campaign", "description": "Testing analytics"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Arannis",
            "role": "PC",
            "class_name": "Ranger",
            "level": 4,
            "max_hp": 32,
            "current_hp": 32,
            "armor_class": 15,
            "notes": None
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Analytics Session",
            "notes": "Testing analytics routes",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Medium",
            "rounds": 4,
            "notes": "Testing damage aggregation"
        }
    ).json()

    arannis = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 32,
            "spell_slots_1": 2,
            "spell_slots_2": 1,
            "spell_slots_3": 0,
            "notes": None
        }
    ).json()

    goblin_boss = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Goblin Boss",
            "participant_type": "OTHER",
            "class_name": "Goblin",
            "max_hp": 21,
            "current_hp": 21,
            "notes": None
        }
    ).json()

    goblin_2 = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Goblin 2",
            "participant_type": "OTHER",
            "class_name": "Goblin",
            "max_hp": 7,
            "current_hp": 7,
            "notes": None
        }
    ).json()

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": arannis["id"],
            "target_participant_id": goblin_boss["id"],
            "amount": 12,
            "spell_slots_consumed": None,
            "detail": "Longbow"
        }
    )

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": arannis["id"],
            "target_participant_id": goblin_2["id"],
            "amount": 9,
            "spell_slots_consumed": None,
            "detail": "Second shot"
        }
    )

    response = client.get(f"/api/v1/campaigns/{campaign['id']}/damage-leaderboard")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["source"] == "Arannis"
    assert data[0]["total_damage"] == 21


def test_encounter_review(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Review Campaign", "description": "Testing review"}
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
            "notes": None
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Review Session",
            "notes": None,
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Ogre Fight",
            "expected_difficulty": "Medium",
            "rounds": 4,
            "notes": None
        }
    ).json()

    ezra = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 2,
            "spell_slots_3": 1,
            "notes": None
        }
    ).json()

    ogre = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Ogre",
            "participant_type": "OTHER",
            "class_name": "Ogre",
            "max_hp": 59,
            "current_hp": 59,
            "notes": None
        }
    ).json()

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": ogre["id"],
            "target_participant_id": ezra["id"],
            "amount": 10,
            "spell_slots_consumed": None,
            "detail": "Club hit"
        }
    )

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": ezra["id"],
            "target_participant_id": ogre["id"],
            "amount": 14,
            "spell_slots_consumed": 1,
            "detail": "Chromatic Orb"
        }
    )

    response = client.get(f"/api/v1/encounters/{encounter['id']}/review")
    assert response.status_code == 200

    review = response.json()
    assert review["expected_difficulty"] == "Medium"
    assert "damage" in review["notes"].lower()
    assert "spell slots" in review["notes"].lower()