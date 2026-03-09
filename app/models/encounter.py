from sqlalchemy import ForeignKey, Integer, String
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
    expected_difficulty: Mapped[str | None] = mapped_column(String(50))
    rounds: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(4000))

    session: Mapped["Session"] = relationship(back_populates="encounters")

    events: Mapped[list["Event"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )

    participants: Mapped[list["EncounterParticipant"]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
    )