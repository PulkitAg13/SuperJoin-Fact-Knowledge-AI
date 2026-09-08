import sys
from backend.app.core.database import SessionLocal
from backend.app.models.relationship import FactRelationship
from backend.app.models.processing_issue import ProcessingIssue
from backend.app.models.document import Document

sys.stdout.reconfigure(encoding='utf-8')
db = SessionLocal()

print("=" * 60)
print("DEMONSTRATING THE 4 REQUIRED CASES ON REAL STARTER DATASET")
print("=" * 60)

# 1. Corroboration
corrob = db.query(FactRelationship).filter(FactRelationship.relationship_type == 'CORROBORATES').first()
if corrob:
    fa, fb = corrob.fact_a, corrob.fact_b
    doc_a = db.query(Document).filter(Document.id == fa.document_id).first()
    doc_b = db.query(Document).filter(Document.id == fb.document_id).first()
    print("\n--- CASE 1: CORROBORATION ---")
    print(f"Fact A [{doc_a.filename} p.{fa.evidence_page}]: {fa.subject} | {fa.predicate} = {fa.object_value} ({fa.temporal_context})")
    print(f"  Evidence A: \"{fa.evidence_text[:150]}...\"")
    print(f"Fact B [{doc_b.filename} p.{fb.evidence_page}]: {fb.subject} | {fb.predicate} = {fb.object_value} ({fb.temporal_context})")
    print(f"  Evidence B: \"{fb.evidence_text[:150]}...\"")
    print(f"Reasoning: {corrob.reasoning}")

# 2. Genuine Contradiction
contra = db.query(FactRelationship).filter(FactRelationship.relationship_type == 'CONTRADICTS').first()
if contra:
    fa, fb = contra.fact_a, contra.fact_b
    doc_a = db.query(Document).filter(Document.id == fa.document_id).first()
    doc_b = db.query(Document).filter(Document.id == fb.document_id).first()
    print("\n--- CASE 2: GENUINE CONTRADICTION ---")
    print(f"Fact A [{doc_a.filename} p.{fa.evidence_page}]: {fa.subject} | {fa.predicate} = {fa.object_value} ({fa.temporal_context})")
    print(f"  Evidence A: \"{fa.evidence_text[:150]}...\"")
    print(f"Fact B [{doc_b.filename} p.{fb.evidence_page}]: {fb.subject} | {fb.predicate} = {fb.object_value} ({fb.temporal_context})")
    print(f"  Evidence B: \"{fb.evidence_text[:150]}...\"")
    print(f"Reasoning: {contra.reasoning}")

# 3. Reconciled by Context
reconc = db.query(FactRelationship).filter(FactRelationship.relationship_type == 'RECONCILED_BY_CONTEXT').first()
if reconc:
    fa, fb = reconc.fact_a, reconc.fact_b
    doc_a = db.query(Document).filter(Document.id == fa.document_id).first()
    doc_b = db.query(Document).filter(Document.id == fb.document_id).first()
    print("\n--- CASE 3: APPARENT CONTRADICTION RECONCILED BY CONTEXT ---")
    print(f"Fact A [{doc_a.filename} p.{fa.evidence_page}]: {fa.subject} | {fa.predicate} = {fa.object_value} ({fa.temporal_context})")
    print(f"  Evidence A: \"{fa.evidence_text[:150]}...\"")
    print(f"Fact B [{doc_b.filename} p.{fb.evidence_page}]: {fb.subject} | {fb.predicate} = {fb.object_value} ({fb.temporal_context})")
    print(f"  Evidence B: \"{fb.evidence_text[:150]}...\"")
    print(f"Reasoning: {reconc.reasoning}")
    print(f"Context Nuance: {reconc.context_explanation}")

# 4. Extraction / Reasoning Failure or Uncertainty
print("\n--- CASE 4: EXTRACTION & REASONING FAILURE / UNCERTAINTY ---")
for iss in db.query(ProcessingIssue).limit(3).all():
    doc = db.query(Document).filter(Document.id == iss.document_id).first()
    print(f"Issue [{doc.filename if doc else 'General'} p.{iss.page_number}]: [{iss.severity}] {iss.category}")
    print(f"  Description: {iss.description}")
    if iss.raw_snippet:
        print(f"  Raw Snippet: \"{iss.raw_snippet[:100]}...\"")

db.close()
