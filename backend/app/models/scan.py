from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Enum, Uuid
from .base import BaseModel
import enum
import uuid


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(BaseModel):
    __tablename__ = "scans"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True)
    image_url: Mapped[str] = mapped_column(String)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), default=ScanStatus.PENDING
    )

    # Relationships
    user = relationship("User", back_populates="scans")
    predictions = relationship(
        "Prediction", back_populates="scan", cascade="all, delete-orphan"
    )
