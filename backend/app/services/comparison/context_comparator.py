from typing import Optional, Dict, Any, List
from backend.app.models.fact import Fact

class ContextComparator:
    @staticmethod
    def compare_contexts(fact_a: Fact, fact_b: Fact) -> Dict[str, Any]:
        """
        Analyzes contextual alignment across time, scope, geography, and units.
        Identifies whether differing values are reconciled by contextual divergence.
        """
        reconciling_factors: List[str] = []
        context_explanations: List[str] = []

        # 1. Temporal Context Comparison
        temp_a = fact_a.temporal_context
        temp_b = fact_b.temporal_context

        temporal_status = "SAME"
        if temp_a and temp_b:
            if temp_a.upper() != temp_b.upper():
                temporal_status = "DIFFERENT"
                reconciling_factors.append("reporting_period")
                context_explanations.append(
                    f"Temporal periods differ: Fact A applies to '{temp_a}' whereas Fact B applies to '{temp_b}'."
                )
        elif bool(temp_a) != bool(temp_b):
            temporal_status = "ONE_UNKNOWN"
            context_explanations.append(
                f"One fact specifies period '{temp_a or temp_b}' while the other does not explicitly declare a period."
            )
        else:
            temporal_status = "BOTH_UNKNOWN"

        # 2. Scope Context Comparison (e.g., Consolidated vs Standalone vs Express Parcel)
        scope_a = fact_a.scope_context
        scope_b = fact_b.scope_context

        scope_status = "SAME"
        if scope_a and scope_b and scope_a.lower() != scope_b.lower():
            scope_status = "DIFFERENT"
            reconciling_factors.append("scope_segment")
            context_explanations.append(
                f"Scope or reporting segment differs: Fact A is '{scope_a}' while Fact B is '{scope_b}'."
            )

        # 3. Geographic Context Comparison
        geo_a = fact_a.geographic_context
        geo_b = fact_b.geographic_context

        geo_status = "SAME"
        if geo_a and geo_b and geo_a.lower() != geo_b.lower():
            geo_status = "DIFFERENT"
            reconciling_factors.append("geographic_scope")
            context_explanations.append(
                f"Geographic scope differs: Fact A refers to '{geo_a}' while Fact B refers to '{geo_b}'."
            )

        has_reconciliation = len(reconciling_factors) > 0

        if has_reconciliation:
            combined_explanation = (
                "Contextual divergence detected: " + "; ".join(context_explanations)
            )
        else:
            combined_explanation = "Contexts are aligned or identically scoped."

        return {
            "has_reconciliation": has_reconciliation,
            "reconciling_factors": reconciling_factors,
            "temporal_status": temporal_status,
            "scope_status": scope_status,
            "geo_status": geo_status,
            "explanation": combined_explanation
        }
