import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.fact import Fact
from backend.app.models.relationship import FactRelationship
from backend.app.models.processing_issue import ProcessingIssue
from backend.app.services.comparison.numerical_comparator import NumericalComparator
from backend.app.services.comparison.context_comparator import ContextComparator
from backend.app.services.comparison.candidate_retriever import CandidateRetriever
from backend.app.services.llm.provider import get_llm_provider

logger = logging.getLogger(__name__)

class RelationshipClassifier:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()

    def classify_pair(self, fact_a: Fact, fact_b: Fact) -> Optional[Dict[str, Any]]:
        """
        Synthesizes numerical comparison, context alignment, and semantic reasoning
        to produce a classified relationship between two facts.
        """
        # Compare contexts
        context_result = ContextComparator.compare_contexts(fact_a, fact_b)
        has_reconciliation = context_result["has_reconciliation"]
        context_explanation = context_result["explanation"]

        # Check if values are numerical
        num_comp = NumericalComparator.compare(
            fact_a.normalized_value,
            fact_b.normalized_value,
            fact_a.unit,
            fact_b.unit
        )

        rel_type = "UNCERTAIN"
        confidence = 0.85
        reasoning = ""

        if num_comp["is_numerical"]:
            if num_comp["is_equivalent"]:
                # Values are numerically equivalent!
                # If contexts are identical or aligned -> CORROBORATES
                if not has_reconciliation:
                    rel_type = "CORROBORATES"
                    confidence = 0.95
                    reasoning = (
                        f"Both documents report equivalent normalized values ({fact_a.normalized_value:,.2f}) "
                        f"for '{fact_a.predicate}' of '{fact_a.subject}' under consistent context."
                    )
                else:
                    # Same number across different periods (e.g. constant value)
                    rel_type = "CORROBORATES"
                    confidence = 0.88
                    reasoning = (
                        f"Equivalent numerical values ({fact_a.normalized_value:,.2f}) reported across documents. "
                        f"Note contextual nuance: {context_explanation}"
                    )
            else:
                # Values diverge / conflict
                if has_reconciliation:
                    # Apparent contradiction reconciled by context! (CASE 3)
                    rel_type = "RECONCILED_BY_CONTEXT"
                    confidence = 0.92
                    reasoning = (
                        f"The values appear contradictory at first glance ({fact_a.object_value} vs {fact_b.object_value}), "
                        f"but the divergence is fully reconciled by contextual differences: {context_explanation}"
                    )
                else:
                    # Same context, conflicting numbers -> GENUINE CONTRADICTION! (CASE 2)
                    rel_type = "CONTRADICTS"
                    confidence = 0.94
                    reasoning = (
                        f"Genuine contradiction detected for '{fact_a.predicate}' of '{fact_a.subject}'. "
                        f"Document A reports '{fact_a.object_value}' while Document B reports '{fact_b.object_value}' "
                        f"under overlapping or identical context ({fact_a.temporal_context or 'unspecified'})."
                    )
        else:
            # Non-numerical semantic comparison (e.g. CEO names, addresses, roles, status)
            val_a_norm = (fact_a.normalized_value_text or fact_a.object_value).strip().lower()
            val_b_norm = (fact_b.normalized_value_text or fact_b.object_value).strip().lower()

            # Exact or substring semantic match
            if val_a_norm == val_b_norm or val_a_norm in val_b_norm or val_b_norm in val_a_norm:
                rel_type = "CORROBORATES"
                confidence = 0.92
                reasoning = (
                    f"Both documents corroborate that the '{fact_a.predicate}' for '{fact_a.subject}' "
                    f"is '{fact_a.object_value}'."
                )
            else:
                # Different semantic claims
                if has_reconciliation:
                    rel_type = "RECONCILED_BY_CONTEXT"
                    confidence = 0.86
                    reasoning = (
                        f"Different statements ('{fact_a.object_value}' vs '{fact_b.object_value}') "
                        f"are reconciled by contextual divergence: {context_explanation}"
                    )
                elif fact_a.confidence < 0.75 or fact_b.confidence < 0.75:
                    rel_type = "UNCERTAIN"
                    confidence = 0.60
                    reasoning = (
                        f"Uncertain whether '{fact_a.object_value}' and '{fact_b.object_value}' "
                        f"represent a genuine conflict due to extraction ambiguity or low source confidence."
                    )
                else:
                    rel_type = "CONTRADICTS"
                    confidence = 0.88
                    reasoning = (
                        f"Conflicting statements for '{fact_a.predicate}' of '{fact_a.subject}': "
                        f"'{fact_a.object_value}' vs '{fact_b.object_value}'."
                    )

        # If confidence is low or comparison is UNCERTAIN, log an issue
        if rel_type == "UNCERTAIN":
            self.db.add(ProcessingIssue(
                document_id=fact_a.document_id,
                category="CONFLICT_UNCERTAIN",
                severity="INFO",
                page_number=fact_a.evidence_page,
                description=f"Comparison between Fact '{fact_a.subject}: {fact_a.predicate}' and '{fact_b.subject}: {fact_b.predicate}' resulted in UNCERTAIN status.",
                raw_snippet=f"Fact A: {fact_a.evidence_text[:100]} | Fact B: {fact_b.evidence_text[:100]}",
                confidence=confidence
            ))

        return {
            "fact_a_id": fact_a.id,
            "fact_b_id": fact_b.id,
            "relationship_type": rel_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "context_explanation": context_explanation
        }

    def analyze_all_facts(self) -> List[FactRelationship]:
        """
        Retrieves candidate pairs across all documents in the database,
        classifies their relationships, and updates the database.
        """
        # Clear existing relationships to re-analyze cleanly
        self.db.query(FactRelationship).delete()
        self.db.commit()

        facts = self.db.query(Fact).all()
        if len(facts) < 2:
            return []

        candidates = CandidateRetriever.get_candidate_pairs(facts)
        relationships = []
        seen_pairs = set()

        for fa, fb in candidates:
            pair_key = tuple(sorted([fa.id, fb.id]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            classified = self.classify_pair(fa, fb)
            if classified and classified["relationship_type"] != "NO_RELATION":
                rel = FactRelationship(
                    fact_a_id=classified["fact_a_id"],
                    fact_b_id=classified["fact_b_id"],
                    relationship_type=classified["relationship_type"],
                    confidence=classified["confidence"],
                    reasoning=classified["reasoning"],
                    context_explanation=classified["context_explanation"]
                )
                self.db.add(rel)
                relationships.append(rel)

        self.db.commit()
        return relationships
