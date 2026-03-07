from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    encounter_id: Mapped[int] = mapped_column(
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False
    )

    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str | None] = mapped_column(String(200))
    target: Mapped[str | None] = mapped_column(String(200))
    amount: Mapped[int | None] = mapped_column(Integer)
    detail: Mapped[str | None] = mapped_column(String(4000))

    encounter: Mapped["Encounter"] = relationship(back_populates="events")