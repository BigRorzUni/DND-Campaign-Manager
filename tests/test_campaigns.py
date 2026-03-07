def test_create_campaign(client):
    response = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Test Campaign",
            "description": "A campaign for testing"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test Campaign"
    assert data["description"] == "A campaign for testing"


def test_list_campaigns(client):
    client.post(
        "/api/v1/campaigns",
        json={
            "name": "Campaign One",
            "description": "First"
        }
    )

    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Campaign One"


def test_get_missing_campaign_returns_404(client):
    response = client.get("/api/v1/campaigns/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"


def test_update_campaign(client):
    create_response = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Old Name",
            "description": "Old description"
        }
    )
    campaign_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/campaigns/{campaign_id}",
        json={
            "name": "New Name",
            "description": "New description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["description"] == "New description"


def test_delete_campaign(client):
    create_response = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Delete Me",
            "description": "Temporary"
        }
    )
    campaign_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/campaigns/{campaign_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert get_response.status_code == 404