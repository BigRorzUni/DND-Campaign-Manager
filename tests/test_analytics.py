def test_campaign_analytics_summary(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Analytics Campaign", "description": "Testing analytics"}
    ).json()

    ezra_character = client.post(
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

    thalia_character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Thalia",
            "role": "PC",
            "class_name": "Fighter",
            "level": 4,
            "max_hp": 30,
            "current_hp": 30,
            "armor_class": 17,
            "notes": None
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Analytics Session",
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
            "character_id": ezra_character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 2,
            "spell_slots_3": 1,
            "notes": None
        }
    ).json()

    thalia = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": thalia_character["id"],
            "participant_type": "PARTY",
            "current_hp": 30,
            "spell_slots_1": 0,
            "spell_slots_2": 0,
            "spell_slots_3": 0,
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
            "spell_slot_level_used": None,
            "detail": "Club hit"
        }
    )

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": ogre["id"],
            "target_participant_id": thalia["id"],
            "amount": 8,
            "spell_slots_consumed": None,
            "spell_slot_level_used": None,
            "detail": "Backhand"
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
            "spell_slot_level_used": 1,
            "detail": "Chromatic Orb"
        }
    )

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "HEAL",
            "source_participant_id": ezra["id"],
            "target_participant_id": thalia["id"],
            "amount": 4,
            "spell_slots_consumed": 1,
            "spell_slot_level_used": 1,
            "detail": "Healing Word"
        }
    )

    time_played_response = client.get(
        f"/api/v1/analytics/campaigns/{campaign['id']}/time-played"
    )
    assert time_played_response.status_code == 200
    time_played = time_played_response.json()
    assert time_played["total_minutes"] == 180
    assert time_played["total_hours"] == 3

    damage_dealt_response = client.get(
        f"/api/v1/analytics/campaigns/{campaign['id']}/damage-leaderboard"
    )
    assert damage_dealt_response.status_code == 200
    damage_dealt = damage_dealt_response.json()
    assert len(damage_dealt) == 1
    assert damage_dealt[0]["source"] == "Ezra"
    assert damage_dealt[0]["total_damage"] == 14

    damage_taken_response = client.get(
        f"/api/v1/analytics/campaigns/{campaign['id']}/damage-taken"
    )
    assert damage_taken_response.status_code == 200
    damage_taken = damage_taken_response.json()

    damage_taken_by_name = {
        row["target"]: row["total_damage_taken"]
        for row in damage_taken
    }

    assert damage_taken_by_name["Ezra"] == 10
    assert damage_taken_by_name["Thalia"] == 8

    healing_received_response = client.get(
        f"/api/v1/analytics/campaigns/{campaign['id']}/healing-received"
    )
    assert healing_received_response.status_code == 200
    healing_received = healing_received_response.json()
    assert len(healing_received) == 1
    assert healing_received[0]["target"] == "Thalia"
    assert healing_received[0]["total_healing_received"] == 4

    spell_usage_response = client.get(
        f"/api/v1/analytics/campaigns/{campaign['id']}/spell-usage"
    )
    assert spell_usage_response.status_code == 200
    spell_usage = spell_usage_response.json()
    assert len(spell_usage) == 1
    assert spell_usage[0]["source"] == "Ezra"
    assert spell_usage[0]["total_spell_slots_used"] == 2