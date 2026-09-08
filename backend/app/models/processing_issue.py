import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ProcessingIssue(Base):
    __tablename__ = "processing_issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    
    # Issue category: OCR_FAILURE, TABLE_PARSING_WARNING, LOW_CONFIDENCE_EXTRACTION, ENTITY_AMBIGUITY, CONFLICT_UNCERTAIN
    category = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), default="WARNING")  # INFO, WARNING, ERROR
    page_number = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    raw_snippet = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="issues")
