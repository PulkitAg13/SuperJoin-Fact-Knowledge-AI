from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.relationship import RelationshipResponse

class ProcessingIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: Optional[str] = None
    category: str
    severity: str
    page_number: Optional[int] = None
    description: str
    raw_snippet: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    document_name: Optional[str] = None

class SystemSummary(BaseModel):
    total_documents: int
    total_facts: int
    total_relationships: int
    corroborations: int
    contradictions: int
    reconciled_cases: int
    uncertain_cases: int
    total_issues: int
    recent_relationships: List[RelationshipResponse] = []
