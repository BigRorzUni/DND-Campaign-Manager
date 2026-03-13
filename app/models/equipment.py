from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)

    api_index: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weapon_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    damage_dice: Mapped[str | None] = mapped_column(String(100), nullable=True)
    damage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    range_normal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    range_long: Mapped[int | None] = mapped_column(Integer, nullable=True)

    armor_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    armor_class_base: Mapped[int | None] = mapped_column(Integer, nullable=True)
    armor_dex_bonus: Mapped[bool | None] = mapped_column(nullable=True)
    armor_max_bonus: Mapped[int | None] = mapped_column(Integer, nullable=True)

    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    brief_description: Mapped[str | None] = mapped_column(Text, nullable=True)