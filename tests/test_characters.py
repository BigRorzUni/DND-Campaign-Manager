def test_create_and_get_character(client, campaign):
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
            "spell_indices": [],
            "equipment_indices": [],
            "spell_slots_1": None,
            "spell_slots_2": None,
            "spell_slots_3": None,
            "spell_slots_4": None,
            "spell_slots_5": None,
            "spell_slots_6": None,
            "spell_slots_7": None,
            "spell_slots_8": None,
            "spell_slots_9": None,
            "notes": "Archer build",
        },
    )

    assert create_response.status_code == 201
    character = create_response.json()

    get_response = client.get(f"/api/v1/characters/{character['id']}")
    assert get_response.status_code == 200
    data = get_response.json()

    assert data["name"] == "Arannis"
    assert data["class_name"] == "Ranger"
    assert data["spell_indices"] == []
    assert data["equipment_indices"] == []


def test_update_character(client, wizard_character):
    response = client.put(
        f"/api/v1/characters/{wizard_character['id']}",
        json={
            "level": 6,
            "current_hp": 20,
            "notes": "Updated after rest",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 6
    assert data["current_hp"] == 20
    assert data["notes"] == "Updated after rest"


def test_delete_character(client, wizard_character):
    delete_response = client.delete(f"/api/v1/characters/{wizard_character['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/characters/{wizard_character['id']}")
    assert get_response.status_code == 404