def test_campaign_analytics_exclude_simulated_encounters(
    client,
    campaign,
    session,
    wizard_character,
):
    normal = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Normal",
            "expected_difficulty": "Medium",
            "notes": None,
            "is_simulated": False,
        },
    ).json()

    simulated = client.post(
        f"/api/v1/sessions/{session['id']}/encounters",
        json={
            "name": "Simulated",
            "expected_difficulty": "Medium",
            "notes": None,
            "is_simulated": True,
        },
    ).json()

    normal_party = client.post(
        f"/api/v1/encounters/{normal['id']}/participants",
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

    normal_enemy = client.post(
        f"/api/v1/encounters/{normal['id']}/participants",
        json={
            "monster_index": "goblin",
            "participant_type": "ENEMY",
        },
    ).json()

    sim_party = client.post(
        f"/api/v1/encounters/{simulated['id']}/participants",
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

    sim_enemy = client.post(
        f"/api/v1/encounters/{simulated['id']}/participants",
        json={
            "monster_index": "goblin",
            "participant_type": "ENEMY",
        },
    ).json()

    client.post(
        f"/api/v1/encounters/{normal['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": normal_party["id"],
            "target_participant_id": normal_enemy["id"],
            "amount": 10,
            "action_type": "custom",
            "action_ref": "custom",
            "detail": "Normal event",
        },
    )

    # Simulated encounter event should not count toward campaign analytics
    client.post(
        f"/api/v1/encounters/{simulated['id']}/events",
        json={
            "kind": "DAMAGE",
            "source_participant_id": sim_party["id"],
            "target_participant_id": sim_enemy["id"],
            "amount": 50,
            "action_type": "custom",
            "action_ref": "custom",
            "detail": "Sim event",
        },
    )

    response = client.get(f"/api/v1/analytics/campaigns/{campaign['id']}/damage-leaderboard")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["source"] == "Ezra"
    assert data[0]["total_damage"] == 10