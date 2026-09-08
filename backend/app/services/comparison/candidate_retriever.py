from collections import defaultdict
from typing import List, Tuple
from backend.app.models.fact import Fact

class CandidateRetriever:
    @staticmethod
    def get_candidate_pairs(facts: List[Fact]) -> List[Tuple[Fact, Fact]]:
        """
        Retrieves pairs of facts across different documents (or distinct records)
        that are likely related based on normalized predicate and entity blocking.
        Prevents full O(N^2) comparison.
        """
        pairs = []
        seen_pairs = set()

        # Block 1: Group by normalized_predicate
        predicate_buckets = defaultdict(list)
        for f in facts:
            predicate_buckets[f.normalized_predicate].append(f)

        for pred, group in predicate_buckets.items():
            if len(group) < 2:
                continue

            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    fa = group[i]
                    fb = group[j]

                    # Prioritize cross-document comparisons
                    # (or cross-temporal within the same doc if checking historical trend)
                    if fa.document_id == fb.document_id and fa.temporal_context == fb.temporal_context:
                        continue

                    # Entity compatibility check:
                    # Either same normalized entity or compatible domain
                    if fa.normalized_subject == fb.normalized_subject or "delhivery" in fa.normalized_subject and "delhivery" in fb.normalized_subject:
                        pair_id = tuple(sorted([fa.id, fb.id]))
                        if pair_id not in seen_pairs:
                            seen_pairs.add(pair_id)
                            pairs.append((fa, fb))
                    elif fa.normalized_predicate in ["gdp_growth_rate", "inflation_rate"]:
                        # Macroeconomic facts for India can compare across economic survey / rbi / imf
                        pair_id = tuple(sorted([fa.id, fb.id]))
                        if pair_id not in seen_pairs:
                            seen_pairs.add(pair_id)
                            pairs.append((fa, fb))

        # Block 2: Cross-check high-value corporate metrics across documents
        # even if predicates had minor variations
        doc_grouped = defaultdict(list)
        for f in facts:
            doc_grouped[f.document_id].append(f)

        doc_ids = list(doc_grouped.keys())
        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                doc_a_facts = doc_grouped[doc_ids[i]]
                doc_b_facts = doc_grouped[doc_ids[j]]
                for fa in doc_a_facts:
                    for fb in doc_b_facts:
                        pair_id = tuple(sorted([fa.id, fb.id]))
                        if pair_id in seen_pairs:
                            continue

                        # Require BOTH entity compatibility and predicate compatibility
                        entity_compatible = (
                            fa.normalized_subject == fb.normalized_subject or
                            ("delhivery" in fa.normalized_subject and "delhivery" in fb.normalized_subject) or
                            (fa.normalized_predicate in ["gdp_growth_rate", "inflation_rate"] and fb.normalized_predicate in ["gdp_growth_rate", "inflation_rate"])
                        )
                        pred_compatible = (
                            fa.normalized_predicate == fb.normalized_predicate or
                            fa.normalized_predicate in fb.normalized_predicate or
                            fb.normalized_predicate in fa.normalized_predicate
                        )
                        if entity_compatible and pred_compatible:
                            seen_pairs.add(pair_id)
                            pairs.append((fa, fb))

        return pairs
