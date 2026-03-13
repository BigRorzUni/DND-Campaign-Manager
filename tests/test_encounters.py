def test_create_normal_encounter(client, session):
    response = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Medium",
            "notes": "Forest road",
            "is_simulated": False,
        },
    )

    assert response.status_code == 201
    encounter = response.json()
    assert encounter["name"] == "Goblin Ambush"
    assert encounter["is_simulated"] is False
    assert encounter["rounds"] is None


def test_create_simulated_encounter(client, session):
    response = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Simulated Goblin Ambush",
            "expected_difficulty": "Medium",
            "notes": "Simulation",
            "is_simulated": True,
        },
    )

    assert response.status_code == 201
    encounter = response.json()
    assert encounter["is_simulated"] is True
    assert encounter["simulation_status"] == "PENDING"