def test_damage_leaderboard(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Analytics Campaign", "description": "Testing analytics"}
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Analytics Session",
            "notes": "Testing analytics routes",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Goblin Ambush",
            "expected_difficulty": "Medium",
            "rounds": 4,
            "notes": "Testing damage aggregation"
        }
    ).json()

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source": "Arannis",
            "target": "Goblin Boss",
            "amount": 12,
            "detail": "Longbow"
        }
    )

    client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source": "Arannis",
            "target": "Goblin 2",
            "amount": 9,
            "detail": "Second shot"
        }
    )

    response = client.get(f"/api/v1/analytics/campaigns/{campaign['id']}/damage-leaderboard")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["source"] == "Arannis"
    assert data[0]["total_damage"] == 21