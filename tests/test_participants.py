def test_create_linked_party_participant(client, normal_encounter, wizard_character):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/participants",
        json={
            "character_id": wizard_character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "notes": "Ready for combat",
        },
    )

    assert response.status_code == 201
    participant = response.json()
    assert participant["character_id"] == wizard_character["id"]
    assert participant["name"] == "Ezra"
    assert participant["class_name"] == "Wizard"


def test_import_monster_participant(client, normal_encounter):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/participants",
        json={
            "monster_index": "mage",
            "participant_type": "ENEMY",
        },
    )

    assert response.status_code == 201
    participant = response.json()
    assert participant["monster_index"] == "mage"
    assert participant["name"].lower() == "mage"
    assert participant["armor_class"] is not None
    assert participant["max_hp"] is not None
    assert participant["current_hp"] == participant["max_hp"]