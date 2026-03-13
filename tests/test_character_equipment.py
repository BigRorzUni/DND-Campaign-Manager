def test_add_equipment_to_character(client, fighter_character):
    response = client.post(
        f"/api/v1/characters/{fighter_character['id']}/equipment",
        json={"equipment_index": "longsword"},
    )
    assert response.status_code == 201

    get_response = client.get(f"/api/v1/characters/{fighter_character['id']}")
    data = get_response.json()
    assert "longsword" in data["equipment_indices"]


def test_cannot_add_duplicate_equipment(client, fighter_character):
    first = client.post(
        f"/api/v1/characters/{fighter_character['id']}/equipment",
        json={"equipment_index": "longsword"},
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/v1/characters/{fighter_character['id']}/equipment",
        json={"equipment_index": "longsword"},
    )
    assert second.status_code in (400, 409)


def test_remove_equipment_from_character(client, fighter_character):
    client.post(
        f"/api/v1/characters/{fighter_character['id']}/equipment",
        json={"equipment_index": "longsword"},
    )

    delete_response = client.delete(
        f"/api/v1/characters/{fighter_character['id']}/equipment/longsword"
    )
    assert delete_response.status_code == 200

    get_response = client.get(f"/api/v1/characters/{fighter_character['id']}")
    data = get_response.json()
    assert "longsword" not in data["equipment_indices"]