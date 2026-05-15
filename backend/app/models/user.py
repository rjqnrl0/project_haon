from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cognito_sub: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    face_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    face_s3_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
