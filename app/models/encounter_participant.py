from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EncounterParticipant(Base):
    __tablename__ = "encounter_participants"

    id: Mapped[int] = mapped_column(primary_key=True)

    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
    )

    character_id: Mapped[int | None] = mapped_column(
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    participant_type: Mapped[str] = mapped_column(String(50), nullable=False)

    class_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)

    monster_index: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    # armor_class: Mapped[int | None] = mapped_column(Integer, nullable=True)


    # immutable encounter-start baseline
    initial_current_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_8: Mapped[int | None] = mapped_column(Integer, nullable=True)
    initial_spell_slots_9: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # mutable derived current state
    current_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_8: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spell_slots_9: Mapped[int | None] = mapped_column(Integer, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    encounter: Mapped["Encounter"] = relationship(back_populates="participants")
    character: Mapped["Character | None"] = relationship()