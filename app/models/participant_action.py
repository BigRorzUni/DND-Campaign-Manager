from sqlalchemy import ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ParticipantAction(Base):
    __tablename__ = "participant_actions"

    id: Mapped[int] = mapped_column(primary_key=True)

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("encounter_participants.id"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTION")

    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)

    attack_bonus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_damage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    damage_dice: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    range_text: Mapped[str | None] = mapped_column(String(200), nullable=True)

    is_dataset_imported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)