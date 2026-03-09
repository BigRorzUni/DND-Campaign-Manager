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
            "participant_type": "ENEMY",
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
            "participant_type": "ENEMY",
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