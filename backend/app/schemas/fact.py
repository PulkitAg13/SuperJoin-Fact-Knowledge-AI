from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class FactBase(BaseModel):
    subject: str = Field(..., description="Entity or concept being described")
    predicate: str = Field(..., description="Property, attribute, or relationship")
    object_value: str = Field(..., description="Original value or statement")
    value_type: str = Field("text", description="number, currency, percentage, date, role, location, status")
    unit: Optional[str] = None
    currency: Optional[str] = None
    temporal_context: Optional[str] = None
    geographic_context: Optional[str] = None
    scope_context: Optional[str] = None
    qualifiers: Optional[str] = None
    confidence: float = 1.0
    evidence_text: str = Field(..., description="Exact textual excerpt from the source document")
    evidence_page: int = Field(..., description="1-indexed source PDF page number")

class FactExtracted(FactBase):
    """Raw extracted fact schema from LLM or heuristic extractor before storage."""
    pass

class FactResponse(FactBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    normalized_subject: str
    normalized_predicate: str
    normalized_value: Optional[float] = None
    normalized_value_text: Optional[str] = None
    evidence_chunk_id: Optional[str] = None
    created_at: datetime
    document_name: Optional[str] = None
