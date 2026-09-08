import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class FactRelationship(Base):
    __tablename__ = "fact_relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fact_a_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)
    fact_b_id = Column(String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Types: CORROBORATES, CONTRADICTS, RECONCILED_BY_CONTEXT, RELATED, UNCERTAIN, NO_RELATION
    relationship_type = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    reasoning = Column(Text, nullable=False)
    context_explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships to Fact objects
    fact_a = relationship("Fact", foreign_keys=[fact_a_id])
    fact_b = relationship("Fact", foreign_keys=[fact_b_id])
