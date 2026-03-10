from sqlalchemy.orm import Session as DbSession

from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event


def _consume_spell_slots(participant: EncounterParticipant, level: int, amount: int) -> None:
    if amount <= 0:
        return

    if level == 1:
        current = participant.spell_slots_1 if participant.spell_slots_1 is not None else 0
        participant.spell_slots_1 = max(0, current - amount)
    elif level == 2:
        current = participant.spell_slots_2 if participant.spell_slots_2 is not None else 0
        participant.spell_slots_2 = max(0, current - amount)
    elif level == 3:
        current = participant.spell_slots_3 if participant.spell_slots_3 is not None else 0
        participant.spell_slots_3 = max(0, current - amount)


def recalculate_encounter_state(db: DbSession, encounter_id: int) -> None:
    participants = (
        db.query(EncounterParticipant)
        .filter(EncounterParticipant.encounter_id == encounter_id)
        .all()
    )

    events = (
        db.query(Event)
        .filter(Event.encounter_id == encounter_id)
        .order_by(Event.id.asc())
        .all()
    )

    participant_map = {p.id: p for p in participants}

    # reset every participant to encounter-start baseline
    for p in participants:
        p.current_hp = p.initial_current_hp
        p.spell_slots_1 = p.initial_spell_slots_1
        p.spell_slots_2 = p.initial_spell_slots_2
        p.spell_slots_3 = p.initial_spell_slots_3

    # replay all events in order
    for e in events:
        source = participant_map.get(e.source_participant_id) if e.source_participant_id else None
        target = participant_map.get(e.target_participant_id) if e.target_participant_id else None

        if e.kind == "DAMAGE" and target and e.amount is not None and target.current_hp is not None:
            target.current_hp = max(0, target.current_hp - e.amount)

        elif e.kind == "HEAL" and target and e.amount is not None and target.current_hp is not None:
            if target.max_hp is not None:
                target.current_hp = min(target.max_hp, target.current_hp + e.amount)
            else:
                target.current_hp = target.current_hp + e.amount

        # spell slot usage can occur on SPELL, DAMAGE, or HEAL events if the DM recorded it
        if (
            source
            and e.spell_slots_consumed is not None
            and e.spell_slots_consumed > 0
            and e.spell_slot_level_used is not None
        ):
            _consume_spell_slots(source, e.spell_slot_level_used, e.spell_slots_consumed)

    db.commit()