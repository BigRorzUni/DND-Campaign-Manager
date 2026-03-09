def test_create_get_and_update_resource_state(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Resource Campaign", "description": "Testing resources"}
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

    # resource state should already exist automatically
    get_response = client.get(f"/api/v1/characters/{character['id']}/resource-state")
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["current_hp"] == 24
    assert data["hit_dice_current"] == 5
    assert data["hit_dice_max"] == 5

    # now update it
    update_response = client.put(
        f"/api/v1/characters/{character['id']}/resource-state",
        json={
            "current_hp": 18,
            "spell_slots_1_current": 4,
            "spell_slots_1_max": 4,
            "spell_slots_2_current": 3,
            "spell_slots_2_max": 3,
            "spell_slots_3_current": 2,
            "spell_slots_3_max": 2
        }
    )
    assert update_response.status_code == 200

    updated = update_response.json()
    assert updated["current_hp"] == 18
    assert updated["spell_slots_2_current"] == 3

def test_character_creation_auto_initialises_resource_state(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Auto Resource Campaign", "description": "Testing auto init"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Mira",
            "role": "PC",
            "class_name": "Cleric",
            "level": 5,
            "max_hp": 36,
            "current_hp": 36,
            "armor_class": 18,
            "notes": "Healer"
        }
    ).json()

    response = client.get(f"/api/v1/characters/{character['id']}/resource-state")
    assert response.status_code == 200
    assert response.json()["character_id"] == character["id"]


def test_create_duplicate_resource_state_returns_400(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Duplicate Resource Campaign", "description": "Testing duplicates"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Mira",
            "role": "PC",
            "class_name": "Cleric",
            "level": 5,
            "max_hp": 36,
            "current_hp": 36,
            "armor_class": 18,
            "notes": "Healer"
        }
    ).json()

    response = client.post(
        f"/api/v1/characters/{character['id']}/resource-state",
        json={"current_hp": 36}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resource state already exists for this character"