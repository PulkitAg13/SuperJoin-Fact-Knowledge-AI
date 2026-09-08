from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.fact import Fact
from backend.app.models.relationship import FactRelationship
from backend.app.models.processing_issue import ProcessingIssue
from backend.app.schemas.analysis import SystemSummary, ProcessingIssueResponse
from backend.app.schemas.relationship import RelationshipResponse
from backend.app.schemas.fact import FactResponse
from backend.app.services.comparison.relationship_classifier import RelationshipClassifier

router = APIRouter(tags=["Analysis"])

def _hydrate_fact(db: Session, fact: Optional[Fact]) -> Optional[FactResponse]:
    if not fact:
        return None
    doc = db.query(Document).filter(Document.id == fact.document_id).first()
    resp = FactResponse.model_validate(fact)
    resp.document_name = doc.filename if doc else "Unknown"
    return resp

@router.post("/analyze")
def trigger_analysis(db: Session = Depends(get_db)):
    """Triggers cross-document comparison and relationship classification across all stored facts."""
    classifier = RelationshipClassifier(db)
    relationships = classifier.analyze_all_facts()
    return {
        "status": "COMPLETED",
        "relationships_discovered": len(relationships)
    }

@router.get("/summary", response_model=SystemSummary)
def get_summary(db: Session = Depends(get_db)):
    """Return system-wide statistics for the dashboard."""
    total_docs = db.query(func.count(Document.id)).scalar() or 0
    total_facts = db.query(func.count(Fact.id)).scalar() or 0
    total_rels = db.query(func.count(FactRelationship.id)).scalar() or 0

    corroborations = db.query(func.count(FactRelationship.id)).filter(
        FactRelationship.relationship_type == "CORROBORATES"
    ).scalar() or 0

    contradictions = db.query(func.count(FactRelationship.id)).filter(
        FactRelationship.relationship_type == "CONTRADICTS"
    ).scalar() or 0

    reconciled = db.query(func.count(FactRelationship.id)).filter(
        FactRelationship.relationship_type == "RECONCILED_BY_CONTEXT"
    ).scalar() or 0

    uncertain = db.query(func.count(FactRelationship.id)).filter(
        FactRelationship.relationship_type == "UNCERTAIN"
    ).scalar() or 0

    total_issues = db.query(func.count(ProcessingIssue.id)).scalar() or 0

    recent_rels_raw = db.query(FactRelationship).order_by(FactRelationship.created_at.desc()).limit(6).all()
    recent_rels = []
    for r in recent_rels_raw:
        recent_rels.append(RelationshipResponse(
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
        ))

    return SystemSummary(
        total_documents=total_docs,
        total_facts=total_facts,
        total_relationships=total_rels,
        corroborations=corroborations,
        contradictions=contradictions,
        reconciled_cases=reconciled,
        uncertain_cases=uncertain,
        total_issues=total_issues,
        recent_relationships=recent_rels
    )

@router.get("/issues", response_model=List[ProcessingIssueResponse])
def list_issues(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    document_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List extraction, OCR, table parsing, or reasoning issues and uncertainties.
    Demonstrates Case 4 (Failure & Uncertainty Handling).
    """
    query = db.query(ProcessingIssue)
    if category:
        query = query.filter(ProcessingIssue.category == category)
    if severity:
        query = query.filter(ProcessingIssue.severity == severity)
    if document_id:
        query = query.filter(ProcessingIssue.document_id == document_id)

    issues = query.order_by(ProcessingIssue.created_at.desc()).limit(limit).all()
    results = []
    for iss in issues:
        doc = db.query(Document).filter(Document.id == iss.document_id).first() if iss.document_id else None
        res = ProcessingIssueResponse.model_validate(iss)
        res.document_name = doc.filename if doc else None
        results.append(res)
    return results
