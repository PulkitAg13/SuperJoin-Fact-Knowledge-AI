from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.fact import Fact
from backend.app.models.document import Document
from backend.app.schemas.fact import FactResponse

router = APIRouter(prefix="/facts", tags=["Facts"])

@router.get("", response_model=List[FactResponse])
def list_facts(
    document_id: Optional[str] = None,
    entity: Optional[str] = None,
    predicate: Optional[str] = None,
    value_type: Optional[str] = None,
    min_confidence: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List facts with flexible search and filtering across entity, predicate,
    document, and confidence thresholds.
    """
    query = db.query(Fact, Document.filename).join(Document, Fact.document_id == Document.id)

    if document_id:
        query = query.filter(Fact.document_id == document_id)
    if entity:
        query = query.filter(Fact.normalized_subject.ilike(f"%{entity}%"))
    if predicate:
        query = query.filter(Fact.normalized_predicate.ilike(f"%{predicate}%"))
    if value_type:
        query = query.filter(Fact.value_type == value_type)
    if min_confidence is not None:
        query = query.filter(Fact.confidence >= min_confidence)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Fact.subject.ilike(search_filter)) |
            (Fact.predicate.ilike(search_filter)) |
            (Fact.object_value.ilike(search_filter)) |
            (Fact.evidence_text.ilike(search_filter))
        )

    items = query.order_by(Fact.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for fact, doc_name in items:
        resp = FactResponse.model_validate(fact)
        resp.document_name = doc_name
        results.append(resp)
    return results


@router.get("/{fact_id}", response_model=FactResponse)
def get_fact(fact_id: str, db: Session = Depends(get_db)):
    """Return full fact details including grounded source evidence."""
    res = db.query(Fact, Document.filename).join(Document, Fact.document_id == Document.id).filter(Fact.id == fact_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Fact not found")
    fact, doc_name = res
    resp = FactResponse.model_validate(fact)
    resp.document_name = doc_name
    return resp
