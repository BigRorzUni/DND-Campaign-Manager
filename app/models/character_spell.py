from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CharacterSpell(Base):
    __tablename__ = "character_spells"

    id: Mapped[int] = mapped_column(primary_key=True)

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        index=True,
        nullable=False
    )

    spell_index: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    spell_name_snapshot: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    spell_level: Mapped[int] = mapped_column(Integer, nullable=False)

    brief_description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)