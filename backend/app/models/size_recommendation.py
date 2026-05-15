import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SizeRecommendation(TimestampMixin, Base):
    __tablename__ = "size_recommendations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    fitting_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fitting_tasks.id", ondelete="CASCADE"), nullable=False
    )
    clothing_category: Mapped[str] = mapped_column(String(20), nullable=False)
    recommended_size: Mapped[str] = mapped_column(String(10), nullable=False)
    size_chart: Mapped[str | None] = mapped_column(Text, nullable=True)
    fit_advice: Mapped[str | None] = mapped_column(Text, nullable=True)
    styling_tip: Mapped[str | None] = mapped_column(Text, nullable=True)
