def test_damage_event_reduces_target_hp_and_can_consume_spell_slots(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Damage Campaign", "description": "Testing DAMAGE"}
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
            "date": "2026-03-09",
            "title": "Combat Session",
            "notes": None,
            "duration_minutes": 120
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Easy",
            "rounds": 2,
            "notes": None
        }
    ).json()

    source_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Spell Goblin",
            "participant_type": "OTHER",
            "class_name": "Goblin Shaman",
            "max_hp": 7,
            "current_hp": 7,
            "spell_slots_1": 2,
            "notes": None
        }
    ).json()

    target_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 32,
            "spell_slots_1": 0,
            "spell_slots_2": 0,
            "spell_slots_3": 0,
            "notes": None
        }
    ).json()

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": source_participant["id"],
            "target_participant_id": target_participant["id"],
            "amount": 5,
            "spell_slots_consumed": 1,
            "spell_slot_level_used": 1,
            "detail": "Inflict Wounds"
        }
    )
    assert response.status_code == 201

    participants = client.get(
        f"/api/v1/encounters/{encounter['id']}/participants"
    ).json()

    updated_source = next(p for p in participants if p["id"] == source_participant["id"])
    updated_target = next(p for p in participants if p["id"] == target_participant["id"])

    assert updated_target["current_hp"] == 27
    assert updated_source["spell_slots_1"] == 1


def test_heal_event_restores_hp_and_can_consume_spell_slots(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Heal Campaign", "description": "Testing HEAL"}
    ).json()

    character = client.post(
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
            "date": "2026-03-09",
            "title": "Healing Session",
            "notes": None,
            "duration_minutes": 120
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Bridge Fight",
            "expected_difficulty": "Medium",
            "rounds": 3,
            "notes": None
        }
    ).json()

    healer_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "name": "Mira",
            "participant_type": "OTHER",
            "class_name": "Cleric",
            "max_hp": 36,
            "current_hp": 36,
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "notes": None
        }
    ).json()

    target_participant = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "participant_type": "PARTY",
            "current_hp": 20,
            "spell_slots_1": 0,
            "spell_slots_2": 0,
            "spell_slots_3": 0,
            "notes": None
        }
    ).json()

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "HEAL",
            "source_participant_id": healer_participant["id"],
            "target_participant_id": target_participant["id"],
            "amount": 15,
            "spell_slots_consumed": 1,
            "spell_slot_level_used": 1,
            "detail": "Cure Wounds"
        }
    )
    assert response.status_code == 201

    participants = client.get(
        f"/api/v1/encounters/{encounter['id']}/participants"
    ).json()

    updated_source = next(p for p in participants if p["id"] == healer_participant["id"])
    updated_target = next(p for p in participants if p["id"] == target_participant["id"])

    assert updated_target["current_hp"] == 30
    assert updated_source["spell_slots_1"] == 3


def test_spell_event_consumes_spell_slots_without_amount(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Spell Campaign", "description": "Testing SPELL"}
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

    caster_participant = client.post(
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

    target_participant = client.post(
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

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "SPELL",
            "source_participant_id": caster_participant["id"],
            "target_participant_id": target_participant["id"],
            "amount": None,
            "spell_slots_consumed": 1,
            "spell_slot_level_used": 1,
            "detail": "Misty Step"
        }
    )
    assert response.status_code == 201

    participants = client.get(
        f"/api/v1/encounters/{encounter['id']}/participants"
    ).json()

    updated_caster = next(p for p in participants if p["id"] == caster_participant["id"])
    assert updated_caster["spell_slots_1"] == 3