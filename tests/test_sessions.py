def test_create_and_list_sessions(client, campaign):
    create_response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/sessions",
        json={
            "date": "2026-03-07",
            "title": "Session 1",
            "notes": "Intro session",
            "duration_minutes": 180,
        },
    )

    assert create_response.status_code == 201
    session_data = create_response.json()
    assert session_data["campaign_id"] == campaign["id"]
    assert session_data["title"] == "Session 1"

    list_response = client.get(f"/api/v1/campaigns/{campaign['id']}/sessions")
    assert list_response.status_code == 200
    sessions = list_response.json()
    assert len(sessions) == 1
    assert sessions[0]["title"] == "Session 1"


def test_create_session_for_missing_campaign_returns_404(client):
    response = client.post(
        "/api/v1/campaigns/999/sessions",
        json={
            "date": "2026-03-07",
            "title": "Bad Session",
            "notes": "Should fail",
            "duration_minutes": 120,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"