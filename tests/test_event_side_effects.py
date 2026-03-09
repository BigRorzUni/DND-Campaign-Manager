def test_damage_event_reduces_target_resource_hp(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Damage Campaign", "description": "Testing DAMAGE"}
    ).json()

    attacker = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Goblin",
            "role": "MONSTER",
            "class_name": None,
            "level": 1,
            "max_hp": 7,
            "current_hp": 7,
            "armor_class": 13,
            "notes": None
        }
    ).json()

    target = client.post(
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

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source": "Goblin",
            "target": "Arannis",
            "source_character_id": attacker["id"],
            "target_character_id": target["id"],
            "amount": 5,
            "slot_level_used": None,
            "detail": "Scimitar hit"
        }
    )
    assert response.status_code == 201

    resource_state = client.get(
        f"/api/v1/characters/{target['id']}/resource-state"
    ).json()

    assert resource_state["current_hp"] == 27


def test_heal_event_restores_hp_but_not_above_max(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Heal Campaign", "description": "Testing HEAL"}
    ).json()

    healer = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Mira",
            "role": "PC",
            "class_name": "Cleric",
            "level": 5,
            "max_hp": 36,
            "current_hp": 36,
            "armor_class": 18,
            "notes": None
        }
    ).json()

    target = client.post(
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

    client.put(
        f"/api/v1/characters/{target['id']}/resource-state",
        json={"current_hp": 20}
    )

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

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "HEAL",
            "source": "Mira",
            "target": "Thalia",
            "source_character_id": healer["id"],
            "target_character_id": target["id"],
            "amount": 15,
            "slot_level_used": None,
            "detail": "Cure Wounds"
        }
    )
    assert response.status_code == 201

    resource_state = client.get(
        f"/api/v1/characters/{target['id']}/resource-state"
    ).json()

    assert resource_state["current_hp"] == 30


def test_spell_event_reduces_spell_slots(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Spell Campaign", "description": "Testing SPELL"}
    ).json()

    caster = client.post(
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

    client.put(
        f"/api/v1/characters/{caster['id']}/resource-state",
        json={
            "current_hp": 24,
            "spell_slots_1_current": 4,
            "spell_slots_1_max": 4,
            "spell_slots_2_current": 2,
            "spell_slots_2_max": 2,
            "spell_slots_3_current": 1,
            "spell_slots_3_max": 1,
            "hit_dice_current": 5,
            "hit_dice_max": 5
        }
    )

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
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "SPELL",
            "source": "Ezra",
            "target": "Ogre",
            "source_character_id": caster["id"],
            "target_character_id": None,
            "amount": None,
            "slot_level_used": 2,
            "slots_consumed": 1,
            "detail": "Scorching Ray"
        }
    )
    assert response.status_code == 201

    resource_state = client.get(
        f"/api/v1/characters/{caster['id']}/resource-state"
    ).json()

    assert resource_state["spell_slots_2_current"] == 1