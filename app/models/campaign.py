from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000))

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan"
    )

    characters: Mapped[list["Character"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan"
    )