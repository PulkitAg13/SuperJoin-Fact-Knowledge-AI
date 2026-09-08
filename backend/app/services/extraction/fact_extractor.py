import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.document import Document, DocumentChunk
from backend.app.models.fact import Fact
from backend.app.models.processing_issue import ProcessingIssue
from backend.app.services.extraction.normalizer import FactNormalizer
from backend.app.services.llm.provider import get_llm_provider

logger = logging.getLogger(__name__)

class FactExtractorService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm_provider()

    def process_document_chunks(
        self,
        document: Document,
        chunks_data: List[Dict[str, Any]],
        extraction_issues: List[Dict[str, Any]]
    ) -> List[Fact]:
        """
        Takes raw chunks and extracted text, extracts grounded facts,
        normalizes them, saves chunks and facts to DB, and records issues.
        """
        # 1. Save extracted issues (e.g., OCR or table parsing warnings)
        for iss in extraction_issues:
            db_issue = ProcessingIssue(
                document_id=document.id,
                category=iss.get("category", "EXTRACTION_WARNING"),
                severity=iss.get("severity", "WARNING"),
                page_number=iss.get("page_number"),
                description=iss.get("description", "Extraction issue detected."),
                raw_snippet=iss.get("raw_snippet")
            )
            self.db.add(db_issue)

        # 2. Save DocumentChunks
        chunk_objects = {}
        for c in chunks_data:
            chunk_obj = DocumentChunk(
                document_id=document.id,
                page_number=c["page_number"],
                chunk_index=c["chunk_index"],
                text=c["text"],
                char_start=c["char_start"],
                char_end=c["char_end"]
            )
            self.db.add(chunk_obj)
            self.db.flush()  # to populate chunk_obj.id
            chunk_objects[(c["page_number"], c["chunk_index"])] = chunk_obj

        # 3. Extract facts from each chunk
        saved_facts = []
        seen_fact_keys = set()

        for c in chunks_data:
            page_num = c["page_number"]
            chunk_idx = c["chunk_index"]
            chunk_text = c["text"]
            chunk_obj = chunk_objects.get((page_num, chunk_idx))

            try:
                raw_facts = self.llm.extract_facts(chunk_text, page_num, document.filename)
            except Exception as e:
                logger.error(f"Error extracting facts on page {page_num}: {e}")
                self.db.add(ProcessingIssue(
                    document_id=document.id,
                    category="EXTRACTION_FAILURE",
                    severity="ERROR",
                    page_number=page_num,
                    description=f"Fact extraction failed on page {page_num}: {str(e)}",
                    raw_snippet=chunk_text[:300]
                ))
                continue

            for rf in raw_facts:
                subj = str(rf.get("subject", "")).strip()
                pred = str(rf.get("predicate", "")).strip()
                val = str(rf.get("object_value", "")).strip()
                ev = str(rf.get("evidence_text", "")).strip()
                conf = float(rf.get("confidence", 0.9))

                if not subj or not pred or not val:
                    continue

                # Ensure evidence text exists; fallback to chunk slice if empty
                if not ev:
                    ev = chunk_text[:250]

                # Normalization
                norm_subj = FactNormalizer.normalize_entity(subj)
                norm_pred = FactNormalizer.normalize_predicate(pred)
                norm_val, norm_val_text, unit, curr = FactNormalizer.normalize_value(
                    val,
                    rf.get("value_type", "text")
                )
                norm_temp = FactNormalizer.normalize_temporal(rf.get("temporal_context"))

                # Deduplication within the document
                dedup_key = (norm_subj, norm_pred, norm_val, norm_val_text, norm_temp, page_num)
                if dedup_key in seen_fact_keys:
                    continue
                seen_fact_keys.add(dedup_key)

                # Low confidence or ambiguous detection
                if conf < 0.70 or norm_subj == "unknown_entity" or norm_pred == "unknown_predicate":
                    self.db.add(ProcessingIssue(
                        document_id=document.id,
                        category="LOW_CONFIDENCE_EXTRACTION" if conf < 0.70 else "ENTITY_AMBIGUITY",
                        severity="WARNING",
                        page_number=page_num,
                        description=f"Ambiguous or low confidence ({conf:.2f}) fact: '{subj}' - '{pred}' = '{val}'",
                        raw_snippet=ev[:300],
                        confidence=conf
                    ))

                fact = Fact(
                    document_id=document.id,
                    subject=subj,
                    predicate=pred,
                    object_value=val,
                    normalized_subject=norm_subj,
                    normalized_predicate=norm_pred,
                    normalized_value=norm_val,
                    normalized_value_text=norm_val_text or str(val),
                    value_type=rf.get("value_type", "text"),
                    unit=unit or rf.get("unit"),
                    currency=curr or rf.get("currency"),
                    temporal_context=norm_temp,
                    geographic_context=rf.get("geographic_context"),
                    scope_context=rf.get("scope_context"),
                    qualifiers=rf.get("qualifiers"),
                    confidence=conf,
                    evidence_text=ev,
                    evidence_page=page_num,
                    evidence_chunk_id=chunk_obj.id if chunk_obj else None
                )
                self.db.add(fact)
                saved_facts.append(fact)

        self.db.commit()
        return saved_facts
