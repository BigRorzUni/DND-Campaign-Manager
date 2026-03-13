def test_add_spell_to_character(client, wizard_character):
    response = client.post(
        f"/api/v1/characters/{wizard_character['id']}/spells",
        json={"spell_index": "magic-missile"},
    )
    assert response.status_code == 201

    get_response = client.get(f"/api/v1/characters/{wizard_character['id']}")
    data = get_response.json()
    assert "magic-missile" in data["spell_indices"]


def test_cannot_add_duplicate_spell(client, wizard_character):
    first = client.post(
        f"/api/v1/characters/{wizard_character['id']}/spells",
        json={"spell_index": "magic-missile"},
    )
    assert first.status_code == 201

    second = client.post(
        f"/api/v1/characters/{wizard_character['id']}/spells",
        json={"spell_index": "magic-missile"},
    )
    assert second.status_code in (400, 409)


def test_remove_spell_from_character(client, wizard_character):
    client.post(
        f"/api/v1/characters/{wizard_character['id']}/spells",
        json={"spell_index": "magic-missile"},
    )

    delete_response = client.delete(
        f"/api/v1/characters/{wizard_character['id']}/spells/magic-missile"
    )
    assert delete_response.status_code == 200

    get_response = client.get(f"/api/v1/characters/{wizard_character['id']}")
    data = get_response.json()
    assert "magic-missile" not in data["spell_indices"]