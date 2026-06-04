from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float, Text, Uuid
from .base import BaseModel
import uuid


class Prediction(BaseModel):
    __tablename__ = "predictions"

    scan_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("scans.id"), index=True)
    condition: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String)
    ai_recommendation: Mapped[str | None] = mapped_column(Text)

    # Relationships
    scan = relationship("Scan", back_populates="predictions")
