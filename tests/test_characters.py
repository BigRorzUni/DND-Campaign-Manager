def test_create_and_list_characters(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Character Campaign",
            "description": "Testing characters"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Arannis",
            "role": "PC",
            "class_name": "Ranger",
            "level": 4,
            "max_hp": 32,
            "current_hp": 28,
            "armor_class": 15,
            "notes": "Archer build"
        }
    )

    assert create_response.status_code == 201
    character = create_response.json()

    assert character["campaign_id"] == campaign["id"]
    assert character["name"] == "Arannis"
    assert character["role"] == "PC"
    assert character["class_name"] == "Ranger"

    list_response = client.get(f"/api/v1/campaigns/{campaign['id']}/characters")
    assert list_response.status_code == 200

    characters = list_response.json()
    assert len(characters) == 1
    assert characters[0]["name"] == "Arannis"


def test_get_character(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Get Character Campaign",
            "description": "Testing get character"
        }
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
            "notes": "Support caster"
        }
    ).json()

    response = client.get(f"/api/v1/characters/{character['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Mira"
    assert data["class_name"] == "Cleric"


def test_update_character(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Update Character Campaign",
            "description": "Testing update character"
        }
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Thalia",
            "role": "PC",
            "class_name": "Fighter",
            "level": 3,
            "max_hp": 30,
            "current_hp": 30,
            "armor_class": 17,
            "notes": "Frontliner"
        }
    ).json()

    response = client.put(
        f"/api/v1/characters/{character['id']}",
        json={
            "level": 4,
            "current_hp": 22,
            "notes": "Updated after level-up"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 4
    assert data["current_hp"] == 22
    assert data["notes"] == "Updated after level-up"


def test_delete_character(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Delete Character Campaign",
            "description": "Testing delete character"
        }
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Ezra",
            "role": "PC",
            "class_name": "Wizard",
            "level": 5,
            "max_hp": 24,
            "current_hp": 20,
            "armor_class": 13,
            "notes": "Glass cannon"
        }
    ).json()

    delete_response = client.delete(f"/api/v1/characters/{character['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/characters/{character['id']}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Character not found"


def test_create_character_for_missing_campaign_returns_404(client):
    response = client.post(
        "/api/v1/campaigns/999/characters",
        json={
            "name": "Ghost",
            "role": "NPC",
            "class_name": "Warlock",
            "level": 2,
            "max_hp": 18,
            "current_hp": 18,
            "armor_class": 12,
            "notes": "Should fail"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"