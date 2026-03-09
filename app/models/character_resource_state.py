from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CharacterResourceState(Base):
    __tablename__ = "character_resource_states"

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    current_hp: Mapped[int | None] = mapped_column(Integer)

    spell_slots_1_current: Mapped[int | None] = mapped_column(Integer)
    spell_slots_1_max: Mapped[int | None] = mapped_column(Integer)

    spell_slots_2_current: Mapped[int | None] = mapped_column(Integer)
    spell_slots_2_max: Mapped[int | None] = mapped_column(Integer)

    spell_slots_3_current: Mapped[int | None] = mapped_column(Integer)
    spell_slots_3_max: Mapped[int | None] = mapped_column(Integer)

    hit_dice_current: Mapped[int | None] = mapped_column(Integer)
    hit_dice_max: Mapped[int | None] = mapped_column(Integer)

    character: Mapped["Character"] = relationship(back_populates="resource_state")