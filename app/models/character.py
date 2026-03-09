from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  
    class_name: Mapped[str | None] = mapped_column(String(100))
    level: Mapped[int | None] = mapped_column(Integer)
    max_hp: Mapped[int | None] = mapped_column(Integer)
    current_hp: Mapped[int | None] = mapped_column(Integer)
    armor_class: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(2000))

    campaign: Mapped["Campaign"] = relationship(back_populates="characters")

    resource_state: Mapped["CharacterResourceState | None"] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
        uselist=False,
    )