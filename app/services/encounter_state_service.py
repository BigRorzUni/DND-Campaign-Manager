from sqlalchemy.orm import Session as DbSession

from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event
from app.services.spell_dataset import SpellDatasetService


def _consume_spell_slots(participant: EncounterParticipant, level: int, amount: int = 1) -> None:
    if amount <= 0 or level <= 0:
        return

    field_name = f"spell_slots_{level}"
    current = getattr(participant, field_name, None)
    current = current if current is not None else 0
    setattr(participant, field_name, max(0, current - amount))


def _get_spell_level(spell_index: str) -> int | None:
    try:
        spell = SpellDatasetService.get_spell(spell_index)
    except Exception:
        return None

    level = spell.get("level")
    return level if isinstance(level, int) else None


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

    # Reset every participant to encounter-start baseline
    for p in participants:
        p.current_hp = p.initial_current_hp
        p.spell_slots_1 = p.initial_spell_slots_1
        p.spell_slots_2 = p.initial_spell_slots_2
        p.spell_slots_3 = p.initial_spell_slots_3
        p.spell_slots_4 = p.initial_spell_slots_4
        p.spell_slots_5 = p.initial_spell_slots_5
        p.spell_slots_6 = p.initial_spell_slots_6
        p.spell_slots_7 = p.initial_spell_slots_7
        p.spell_slots_8 = p.initial_spell_slots_8
        p.spell_slots_9 = p.initial_spell_slots_9

    # Optional small cache so repeated spells don't refetch every time
    spell_level_cache: dict[str, int | None] = {}

    # Replay all events in order
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

        # Infer spell slot usage from action fields
        if source and e.action_type == "spell" and e.action_ref:
            if e.action_ref not in spell_level_cache:
                spell_level_cache[e.action_ref] = _get_spell_level(e.action_ref)

            spell_level = spell_level_cache[e.action_ref]

            # Cantrips are level 0 and consume no slots
            if spell_level is not None and spell_level > 0:
                _consume_spell_slots(source, spell_level, 1)

    db.commit()