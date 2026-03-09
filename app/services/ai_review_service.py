from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.models.encounter import Encounter
from app.models.encounter_participant import EncounterParticipant
from app.models.event import Event


class AiReviewService:
    def __init__(self) -> None:
        self.model = settings.OPENAI_MODEL
        self.enabled = settings.AI_REVIEW_ENABLED

        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None

    def mark_encounter_review_stale(self, db: DbSession, encounter_id: int) -> None:
        encounter = db.get(Encounter, encounter_id)
        if not encounter:
            return
        encounter.ai_review_is_stale = True
        db.commit()

    def build_encounter_summary(
        self,
        db: DbSession,
        encounter_id: int,
    ) -> dict[str, Any]:
        encounter = db.get(Encounter, encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

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

        party_participants = [p for p in participants if p.participant_type == "PARTY"]
        participant_map = {p.id: p for p in participants}
        party_ids = {p.id for p in party_participants}

        party_damage_taken = sum(
            e.amount or 0
            for e in events
            if e.kind == "DAMAGE" and e.target_participant_id in party_ids
        )

        party_healing_received = sum(
            e.amount or 0
            for e in events
            if e.kind == "HEAL" and e.target_participant_id in party_ids
        )

        party_spell_slots_used = sum(
            e.spell_slots_consumed or 0
            for e in events
            if e.source_participant_id in party_ids
        )

        party_zero_hp_count = sum(
            1 for p in party_participants
            if p.current_hp is not None and p.current_hp <= 0
        )

        party_starting_hp_total = sum(p.max_hp or 0 for p in party_participants)
        party_current_hp_total = sum(p.current_hp or 0 for p in party_participants)

        party = []
        for p in party_participants:
            party.append(
                {
                    "name": p.name,
                    "class_name": p.class_name,
                    "level": p.level,
                    "max_hp": p.max_hp,
                    "current_hp_end": p.current_hp,
                    "initial_spell_slots_available": {
                        "level_1": p.spell_slots_1,
                        "level_2": p.spell_slots_2,
                        "level_3": p.spell_slots_3,
                    },
                }
            )

        notable_events: list[str] = []
        for e in events[:20]:
            source_name = participant_map[e.source_participant_id].name if e.source_participant_id in participant_map else "Unknown"
            target_name = participant_map[e.target_participant_id].name if e.target_participant_id in participant_map else "Unknown"

            parts = [f"{e.kind}: {source_name} -> {target_name}"]
            if e.amount is not None:
                parts.append(f"amount={e.amount}")
            if e.spell_slots_consumed is not None:
                parts.append(f"spell_slots_used={e.spell_slots_consumed}")
            if e.detail:
                parts.append(f"detail={e.detail}")

            notable_events.append(" | ".join(parts))

        return {
            "encounter_name": encounter.name,
            "expected_difficulty": encounter.expected_difficulty,
            "rounds": encounter.rounds,
            "party": party,
            "summary_metrics": {
                "party_damage_taken": party_damage_taken,
                "party_healing_received": party_healing_received,
                "party_spell_slots_used": party_spell_slots_used,
                "party_zero_hp_count": party_zero_hp_count,
                "party_starting_hp_total": party_starting_hp_total,
                "party_current_hp_total": party_current_hp_total,
            },
            "notable_events": notable_events,
        }

    def _fallback_review(self) -> dict[str, Any]:
        return {
            "observed_difficulty": "Unavailable",
            "did_meet_intent": "Unavailable",
            "resource_pressure": "Unavailable",
            "reasoning": "AI review unavailable.",
            "dm_advice": "Check AI configuration or billing to enable AI review.",
            "encounter_balance_suggestions": [
                "Enable AI billing to receive encounter balancing suggestions."
            ],
        }

    def _generate_new_review(
        self,
        summary: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.enabled or self.client is None:
            return self._fallback_review()

        schema = {
            "type": "object",
            "properties": {
                "observed_difficulty": {
                    "type": "string",
                    "enum": ["Trivial", "Easy", "Medium", "Hard", "Deadly"],
                },
                "did_meet_intent": {
                    "type": "string",
                    "enum": ["Yes", "No, easier", "No, harder"],
                },
                "resource_pressure": {
                    "type": "string",
                    "enum": ["Low", "Moderate", "High"],
                },
                "reasoning": {"type": "string"},
                "dm_advice": {"type": "string"},
                "encounter_balance_suggestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 5,
                },
            },
            "required": [
                "observed_difficulty",
                "did_meet_intent",
                "resource_pressure",
                "reasoning",
                "dm_advice",
                "encounter_balance_suggestions",
            ],
            "additionalProperties": False,
        }

        prompt = (
            "You are reviewing a DnD encounter for a DM.\n"
            "Use only the provided encounter summary.\n"
            "Judge whether the encounter met its intended difficulty for the party.\n"
            "Party-only cost matters most: damage taken, healing needed, spell slots used, "
            "zero-HP states, and how depleted the party became.\n"
            "Initial spell slots available at the start of the encounter are included so you can "
            "assess resource pressure fairly.\n"
            "Also provide practical encounter balance suggestions for future runs of the same fight.\n"
            "Suggestions should be small, actionable adjustments like enemy count, HP, damage, "
            "action economy, terrain pressure, or resource drain.\n"
            "Be concise and grounded in the provided data.\n\n"
            f"Encounter summary:\n{json.dumps(summary, indent=2)}"
        )

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "encounter_ai_review",
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
        except Exception:
            return self._fallback_review()

        if not response.output_text:
            return self._fallback_review()

        try:
            return json.loads(response.output_text)
        except json.JSONDecodeError:
            return self._fallback_review()

    def get_or_generate_review(
        self,
        db: DbSession,
        encounter_id: int,
        *,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        encounter = db.get(Encounter, encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        if encounter.ai_review_cached and not encounter.ai_review_is_stale and not force_refresh:
            try:
                return json.loads(encounter.ai_review_cached)
            except json.JSONDecodeError:
                encounter.ai_review_cached = None
                encounter.ai_review_is_stale = True
                db.commit()

        summary = self.build_encounter_summary(db, encounter_id)
        review = self._generate_new_review(summary)

        encounter.ai_review_cached = json.dumps(review)
        encounter.ai_review_is_stale = False
        db.commit()

        return review