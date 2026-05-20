import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class WeatherRequest(TimestampMixin, Base):
    __tablename__ = "weather_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    weather_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    codi_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
