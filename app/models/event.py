from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
    )

    kind: Mapped[str] = mapped_column(String(50), nullable=False)

    source_participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("encounter_participants.id", ondelete="SET NULL"),
        nullable=True,
    )

    target_participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("encounter_participants.id", ondelete="SET NULL"),
        nullable=True,
    )

    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # New: used by simulation log grouping
    round_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    action_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action_name_snapshot: Mapped[str | None] = mapped_column(String(200), nullable=True)
    action_description_snapshot: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    encounter: Mapped["Encounter"] = relationship(back_populates="events")