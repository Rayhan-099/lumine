from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    predicted_class = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    text_condition = Column(String, nullable=True)
    text_seriousness = Column(String, nullable=True)
    ai_summary = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    
    # Provenance fields
    inference_status = Column(String, nullable=False, default="legacy_unverified")
    model_id = Column(String, nullable=True)
    inference_provider = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    
    user = relationship("User", backref="analyses")
