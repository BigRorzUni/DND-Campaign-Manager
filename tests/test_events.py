def test_create_and_list_events(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Event Campaign", "description": "Testing events"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Rogue",
            "role": "PC",
            "class_name": "Rogue",
            "level": 4,
            "max_hp": 28,
            "current_hp": 28,
            "armor_class": 15,
            "notes": "Sneaky"
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Event Session",
            "notes": "Testing event logging",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Bandit Fight",
            "expected_difficulty": "Hard",
            "rounds": 5,
            "notes": "Bridge ambush"
        }
    ).json()

    party_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 28,
            "spell_slots_1": 0,
            "spell_slots_2": 0,
            "spell_slots_3": 0,
            "notes": "Ready for combat"
        }
    ).json()

    enemy_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Bandit Captain",
            "participant_type": "ENEMY",
            "class_name": "Bandit",
            "max_hp": 40,
            "current_hp": 40,
            "notes": "Bridge leader"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": party_participant["id"],
            "target_participant_id": enemy_participant["id"],
            "amount": 14,
            "spell_slots_consumed": None,
            "detail": "Sneak attack"
        }
    )

    assert create_response.status_code == 201
    event = create_response.json()
    assert event["kind"] == "DAMAGE"
    assert event["amount"] == 14
    assert event["source_participant_id"] == party_participant["id"]
    assert event["target_participant_id"] == enemy_participant["id"]

    list_response = client.get(f"/api/v1/encounters/{encounter['id']}/events")
    assert list_response.status_code == 200
    events = list_response.json()
    assert len(events) == 1
    assert events[0]["detail"] == "Sneak attack"
    assert events[0]["source_participant_id"] == party_participant["id"]
    assert events[0]["target_participant_id"] == enemy_participant["id"]