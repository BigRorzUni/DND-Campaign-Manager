def test_manual_event_creation_blocked_for_simulated_encounter(
    client,
    simulated_encounter,
    wizard_character,
):
    party = client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants",
        json={
            "character_id": wizard_character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "notes": None,
        },
    ).json()

    enemy = client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants",
        json={
            "monster_index": "goblin",
            "participant_type": "ENEMY",
        },
    ).json()

    actions = client.get(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants/{party['id']}/actions"
    ).json()

    action = actions[0]

    response = client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": party["id"],
            "target_participant_id": enemy["id"],
            "amount": 5,
            "action_type": action["action_type"],
            "action_ref": action["action_ref"],
            "detail": "Should fail",
        },
    )

    assert response.status_code == 400
    assert "simulated" in response.json()["detail"].lower()


def test_run_simulation_updates_encounter(
    client,
    simulated_encounter,
    wizard_character,
    fighter_character,
):
    client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants",
        json={
            "character_id": wizard_character["id"],
            "participant_type": "PARTY",
            "current_hp": 24,
            "spell_slots_1": 4,
            "spell_slots_2": 3,
            "spell_slots_3": 2,
            "notes": None,
        },
    )

    client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants",
        json={
            "character_id": fighter_character["id"],
            "participant_type": "PARTY",
            "current_hp": 30,
            "notes": None,
        },
    )

    client.post(
        f"/api/v1/encounters/{simulated_encounter['id']}/participants",
        json={
            "monster_index": "goblin",
            "participant_type": "ENEMY",
        },
    )

    response = client.post(f"/api/v1/encounters/{simulated_encounter['id']}/simulate")
    assert response.status_code == 200

    updated = client.get(f"/api/v1/encounters/{simulated_encounter['id']}").json()
    assert updated["simulation_status"] == "COMPLETED"
    assert updated["rounds"] is not None
    assert updated["winner"] in ("PARTY", "ENEMY")

    events = client.get(f"/api/v1/encounters/{simulated_encounter['id']}/events").json()
    assert len(events) > 0