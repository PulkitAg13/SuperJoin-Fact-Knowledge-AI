from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.fact import FactResponse

class RelationshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fact_a_id: str
    fact_b_id: str
    relationship_type: str  # CORROBORATES, CONTRADICTS, RECONCILED_BY_CONTEXT, RELATED, UNCERTAIN
    confidence: float
    reasoning: str
    context_explanation: Optional[str] = None
    created_at: datetime
    
    fact_a: Optional[FactResponse] = None
    fact_b: Optional[FactResponse] = None
