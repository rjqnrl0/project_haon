import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class FittingTask(TimestampMixin, Base):
    __tablename__ = "fitting_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)  # fitting | background
    status: Mapped[str] = mapped_column(String(20), default="pending")
    body_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    clothing_file_paths: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    result_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
