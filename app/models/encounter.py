from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    expected_difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rounds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ai_review_cached: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_review_is_stale: Mapped[bool] = mapped_column(nullable=False, default=True)

    # New fields for simulated encounters
    is_simulated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    simulation_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    winner: Mapped[str | None] = mapped_column(String(20), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="encounters")

    participants: Mapped[list["EncounterParticipant"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )