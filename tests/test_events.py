def test_create_damage_event_with_action_snapshots(
    client,
    normal_encounter,
    wizard_participant,
    enemy_participant,
):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": wizard_participant["id"],
            "target_participant_id": enemy_participant["id"],
            "amount": 7,
            "action_type": "custom",
            "action_ref": "custom",
            "detail": "Test damage event",
        },
    )

    assert response.status_code == 201
    event = response.json()
    assert event["action_type"] == "custom"
    assert event["action_ref"] == "custom"


def test_damage_event_reduces_target_hp(
    client,
    normal_encounter,
    wizard_participant,
    enemy_participant,
):
    response = client.post(
        f"/api/v1/encounters/{normal_encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": wizard_participant["id"],
            "target_participant_id": enemy_participant["id"],
            "amount": 5,
            "action_type": "custom",
            "action_ref": "custom",
            "detail": "Damage test",
        },
    )
    assert response.status_code == 201

    participants = client.get(
        f"/api/v1/encounters/{normal_encounter['id']}/participants"
    ).json()

    updated_target = next(p for p in participants if p["id"] == enemy_participant["id"])
    assert updated_target["current_hp"] == enemy_participant["current_hp"] - 5