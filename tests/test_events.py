def test_create_and_list_events(client):
    campaign = client.post(
        "/api/v1/campaigns",
        json={"name": "Event Campaign", "description": "Testing events"}
    ).json()

    session = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Event Session",
            "notes": "Testing event logging",
            "duration_minutes": 180
        }
    ).json()

    encounter = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Bandit Fight",
            "expected_difficulty": "Hard",
            "rounds": 5,
            "notes": "Bridge ambush"
        }
    ).json()

    create_response = client.post(
        f"/api/v1/encounters/{encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source": "Rogue",
            "target": "Bandit Captain",
            "amount": 14,
            "detail": "Sneak attack"
        }
    )

    assert create_response.status_code == 201
    event = create_response.json()
    assert event["kind"] == "DAMAGE"
    assert event["amount"] == 14

    list_response = client.get(f"/api/v1/encounters/{encounter['id']}/events")
    assert list_response.status_code == 200
    events = list_response.json()
    assert len(events) == 1
    assert events[0]["source"] == "Rogue"