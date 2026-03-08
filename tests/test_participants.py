def test_create_and_list_encounter_participants(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Participants Campaign", "description": "Testing participants"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign['id']}/characters",
        json={
            "name": "Arannis",
            "role": "PC",
            "class_name": "Ranger",
            "level": 4,
            "max_hp": 32,
            "current_hp": 28,
            "armor_class": 15,
            "notes": "Archer"
        }
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Session 1",
            "notes": "Participants test",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Easy",
            "rounds": 4,
            "notes": "Roadside ambush"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "starting_hp": 28,
            "starting_hp_percent": 87.5,
            "spell_slots_1_start": 2,
            "spell_slots_2_start": 1,
            "spell_slots_3_start": 0,
            "hit_dice_start": 4,
            "notes": "Slightly injured before combat"
        }
    )

    assert create_response.status_code == 201
    participant = create_response.json()
    assert participant["character_id"] == character["id"]
    assert participant["starting_hp"] == 28

    list_response = client.get(f"/api/v1/encounters/{encounter['id']}/participants")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1
    assert data[0]["character_id"] == character["id"]


def test_create_participant_with_character_from_wrong_campaign_returns_400(client):
    campaign_1 = client.post(
        "/api/v1/campaigns",
        json={"name": "Campaign One", "description": "First"}
    ).json()

    campaign_2 = client.post(
        "/api/v1/campaigns",
        json={"name": "Campaign Two", "description": "Second"}
    ).json()

    character = client.post(
        f"/api/v1/campaigns/{campaign_1['id']}/characters",
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

    session = client.post(
        f"/api/v1/campaigns/{campaign_2['id']}/sessions",
        json={
            "date": "2026-03-08",
            "title": "Session 2",
            "notes": "Wrong campaign test",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Ogre Fight",
            "expected_difficulty": "Medium",
            "rounds": 5,
            "notes": "Bridge fight"
        }
    ).json()

    response = client.post(
        f"/api/v1/encounters/{encounter['id']}/participants",
        json={
            "character_id": character["id"],
            "starting_hp": 36,
            "starting_hp_percent": 100,
            "spell_slots_1_start": 4,
            "spell_slots_2_start": 3,
            "spell_slots_3_start": 2,
            "hit_dice_start": 5,
            "notes": "Should fail"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Character does not belong to the same campaign as this encounter"