def test_create_and_list_encounters(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Encounter Campaign", "description": "Testing encounters"}
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Combat Session",
            "notes": "Encounter tests",
            "duration_minutes": 180
        }
    ).json()

    create_response = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Medium",
            "rounds": 4,
            "notes": "Forest road"
        }
    )

    assert create_response.status_code == 201
    encounter = create_response.json()
    assert encounter["session_id"] == session["id"]
    assert encounter["name"] == "Goblin Ambush"

    list_response = client.get(f"/api/v1/sessions/{session['id']}/encounters")
    assert list_response.status_code == 200
    encounters = list_response.json()
    assert len(encounters) == 1
    assert encounters[0]["name"] == "Goblin Ambush"