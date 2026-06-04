from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum
from .base import BaseModel
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    full_name: Mapped[str | None] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    subscription_tier: Mapped[str] = mapped_column(String, default="free")

    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship(
        "AIConversation", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
