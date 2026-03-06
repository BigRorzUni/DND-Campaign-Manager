from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False
    )

    date: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(4000))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)

    campaign: Mapped["Campaign"] = relationship(back_populates="sessions")

    encounters: Mapped[list["Encounter"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan"
    )