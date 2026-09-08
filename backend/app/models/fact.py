import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Fact(Base):
    __tablename__ = "facts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Core triple (subject, predicate, object)
    subject = Column(String(255), nullable=False)
    predicate = Column(String(255), nullable=False)
    object_value = Column(Text, nullable=False)
    
    # Normalized representation
    normalized_subject = Column(String(255), nullable=False, index=True)
    normalized_predicate = Column(String(255), nullable=False, index=True)
    normalized_value = Column(Float, nullable=True)  # Numeric canonical value if applicable
    normalized_value_text = Column(String(255), nullable=True)  # Normalized text/date
    
    # Metadata & contextual dimensions
    value_type = Column(String(50), default="text")  # number, currency, percentage, date, role, location, status
    unit = Column(String(50), nullable=True)
    currency = Column(String(20), nullable=True)
    
    temporal_context = Column(String(100), nullable=True, index=True)  # e.g., FY2023, 2024, Q4 FY24
    geographic_context = Column(String(100), nullable=True)  # e.g., India, Delhi NCR
    scope_context = Column(String(100), nullable=True)  # e.g., Consolidated, Express Parcel, PTL
    qualifiers = Column(String(100), nullable=True)  # e.g., approximate, reported, estimated
    
    confidence = Column(Float, default=1.0)
    
    # Evidence Grounding
    evidence_text = Column(Text, nullable=False)
    evidence_page = Column(Integer, nullable=False)
    evidence_chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="facts")
    chunk = relationship("DocumentChunk")
