from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EncounterParticipantState(Base):
    __tablename__ = "encounter_participant_states"

    id: Mapped[int] = mapped_column(primary_key=True)

    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
    )

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )

    starting_hp: Mapped[int | None] = mapped_column(Integer)
    starting_hp_percent: Mapped[float | None] = mapped_column(Float)

    spell_slots_1_start: Mapped[int | None] = mapped_column(Integer)
    spell_slots_2_start: Mapped[int | None] = mapped_column(Integer)
    spell_slots_3_start: Mapped[int | None] = mapped_column(Integer)

    hit_dice_start: Mapped[int | None] = mapped_column(Integer)

    notes: Mapped[str | None] = mapped_column(String(1000))

    encounter: Mapped["Encounter"] = relationship(back_populates="participants")
    character: Mapped["Character"] = relationship()