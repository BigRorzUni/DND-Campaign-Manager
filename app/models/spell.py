from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Spell(Base):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(primary_key=True)

    api_index: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    school: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brief_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    range_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    casting_time: Mapped[str | None] = mapped_column(String(100), nullable=True)

    attack_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damage_dice: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    dc_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dc_success: Mapped[str | None] = mapped_column(String(100), nullable=True)