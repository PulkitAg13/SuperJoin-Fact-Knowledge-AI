from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.relationship import FactRelationship
from backend.app.models.fact import Fact
from backend.app.models.document import Document
from backend.app.schemas.relationship import RelationshipResponse
from backend.app.schemas.fact import FactResponse

router = APIRouter(prefix="/relationships", tags=["Relationships"])

def _hydrate_fact(db: Session, fact: Optional[Fact]) -> Optional[FactResponse]:
    if not fact:
        return None
    doc = db.query(Document).filter(Document.id == fact.document_id).first()
    resp = FactResponse.model_validate(fact)
    resp.document_name = doc.filename if doc else "Unknown"
    return resp

@router.get("", response_model=List[RelationshipResponse])
def list_relationships(
    relationship_type: Optional[str] = None,
    document_id: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List cross-document relationships with filters for relationship types:
    CORROBORATES, CONTRADICTS, RECONCILED_BY_CONTEXT, UNCERTAIN.
    """
    query = db.query(FactRelationship)

    if relationship_type and relationship_type != "ALL":
        query = query.filter(FactRelationship.relationship_type == relationship_type)
    if min_confidence is not None:
        query = query.filter(FactRelationship.confidence >= min_confidence)

    rels = query.order_by(FactRelationship.created_at.desc()).limit(limit).all()

    results = []
    for r in rels:
        # Filter by document_id if requested
        if document_id:
            if r.fact_a and r.fact_a.document_id != document_id and r.fact_b and r.fact_b.document_id != document_id:
                continue

        resp = RelationshipResponse(
            id=r.id,
            fact_a_id=r.fact_a_id,
            fact_b_id=r.fact_b_id,
            relationship_type=r.relationship_type,
            confidence=r.confidence,
            reasoning=r.reasoning,
            context_explanation=r.context_explanation,
            created_at=r.created_at,
            fact_a=_hydrate_fact(db, r.fact_a),
            fact_b=_hydrate_fact(db, r.fact_b)
        )
        results.append(resp)

    return results


@router.get("/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: str, db: Session = Depends(get_db)):
    """Return full details, evidence for both facts, and reasoning for a relationship."""
    r = db.query(FactRelationship).filter(FactRelationship.id == relationship_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return RelationshipResponse(
        id=r.id,
        fact_a_id=r.fact_a_id,
        fact_b_id=r.fact_b_id,
        relationship_type=r.relationship_type,
        confidence=r.confidence,
        reasoning=r.reasoning,
        context_explanation=r.context_explanation,
        created_at=r.created_at,
        fact_a=_hydrate_fact(db, r.fact_a),
        fact_b=_hydrate_fact(db, r.fact_b)
    )
