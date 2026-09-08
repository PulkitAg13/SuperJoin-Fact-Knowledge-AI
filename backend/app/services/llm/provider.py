import json
import logging
import re
from typing import List, Dict, Any, Optional
import requests

from backend.app.core.config import settings
from backend.app.services.llm.base import LLMProvider
from backend.app.services.llm.prompts import (
    FACT_EXTRACTION_SYSTEM_PROMPT,
    FACT_COMPARISON_SYSTEM_PROMPT
)
from backend.app.services.extraction.context_extractor import ContextExtractor

logger = logging.getLogger(__name__)

class FallbackRuleBasedProvider(LLMProvider):
    """
    Deterministic rule-based extractor and comparator used when no Gemini API key is present
    or as a fallback mechanism.
    """
    def extract_facts(self, chunk_text: str, page_number: int, document_name: str) -> List[Dict[str, Any]]:
        facts = []
        if not chunk_text or len(chunk_text.strip()) < 20:
            return facts

        # Context detection for the chunk
        context = ContextExtractor.extract_context(chunk_text)
        temporal = context.get("temporal_context")
        scope = context.get("scope_context")
        geo = context.get("geographic_context")

        # Entity identification heuristics
        default_entity = "Entity"
        doc_lower = document_name.lower()
        if "delhivery" in doc_lower or "delhivery" in chunk_text.lower():
            default_entity = "Delhivery"
        elif "rbi" in doc_lower or "reserve bank" in chunk_text.lower():
            default_entity = "Reserve Bank of India"
        elif "economic survey" in doc_lower or "imf" in doc_lower or "india" in chunk_text.lower():
            default_entity = "India Economy"

        # Normalize single line breaks within sentences while preserving paragraph breaks
        cleaned_chunk = re.sub(r'(?<![.!?:\n])\n(?!\n)', ' ', chunk_text)
        # Avoid splitting on decimal points within numbers (e.g. 6.6 per cent)
        lines_or_sentences = [s.strip() for s in re.split(r'(?<!\d)(?<=[.!?])(?!\d)\s+|\n{2,}', cleaned_chunk) if s.strip()]

        for sent in lines_or_sentences:
            sent_clean = " ".join(sent.split())
            if len(sent_clean) < 15:
                continue

            # Check sentence-specific temporal override
            sent_context = ContextExtractor.extract_context(sent_clean)
            sent_temporal = sent_context.get("temporal_context") or temporal

            # 1. Revenue patterns
            # e.g., "Revenue for FY2023 was ₹100 crore", "Revenue was ₹120 crore in FY2023", "generated one hundred crore rupees"
            rev_match = re.search(
                r'(?:revenue(?:\s+from\s+operations)?|turnover|generated)\s+(?:was|of|stood at|reached|during [^\s]+ was)?\s*([₹$€]?\s*(?:[0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?|one hundred)\s*(?:crore|cr|lakh|million|billion|rupees|inr)?)',
                sent_clean,
                re.IGNORECASE
            )
            if rev_match and any(c.isdigit() or w in rev_match.group(1).lower() for w in ["crore", "hundred", "million"] for c in rev_match.group(1)):
                val = rev_match.group(1).strip()
                facts.append({
                    "subject": default_entity,
                    "predicate": "revenue",
                    "object_value": val,
                    "value_type": "currency",
                    "temporal_context": sent_temporal,
                    "scope_context": sent_context.get("scope_context") or scope,
                    "geographic_context": sent_context.get("geographic_context") or geo,
                    "confidence": 0.95,
                    "evidence_text": sent_clean
                })

            # 2. Employee count patterns
            # e.g., "The company has 500 employees", "employs approximately 700 employees", "headcount of 500"
            emp_match = re.search(
                r'(?:has|employs|headcount of|workforce of|team of)\s*(?:approximately|about)?\s*([0-9]+(?:,[0-9]+)?)\s*(?:employees|people|staff)?',
                sent_clean,
                re.IGNORECASE
            )
            if emp_match and "employee" in sent_clean.lower():
                val = emp_match.group(1).strip() + " employees"
                facts.append({
                    "subject": default_entity,
                    "predicate": "employee_count",
                    "object_value": val,
                    "value_type": "number",
                    "temporal_context": sent_temporal,
                    "scope_context": scope,
                    "geographic_context": geo,
                    "confidence": 0.92,
                    "evidence_text": sent_clean
                })

            # 3. Leadership & CEO patterns
            # e.g., "Sahil Barua is the Managing Director and Chief Executive Officer", "appointed Jane Doe as CEO"
            ceo_match = re.search(
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s+(?:is|serves as|appointed as|was appointed as)\s+(?:the\s+)?(?:Managing Director and\s+)?(?:Chief Executive Officer|CEO|Director)',
                sent_clean,
                re.IGNORECASE
            )
            if ceo_match:
                person = ceo_match.group(1).strip()
                facts.append({
                    "subject": default_entity,
                    "predicate": "chief_executive_officer",
                    "object_value": person,
                    "value_type": "role",
                    "temporal_context": sent_temporal,
                    "scope_context": scope,
                    "geographic_context": geo,
                    "confidence": 0.90,
                    "evidence_text": sent_clean
                })

            # 4. GDP Growth / Inflation patterns
            # Matches: "real GDP growth for 2025-26 is projected at 6.6 per cent", "real GDP is projected to grow at 6.6 percent in FY2025/26"
            macro_match = re.search(
                r'\b(real\s+gdp|gdp|economic\s+growth|cpi\s+inflation|headline\s+inflation|core\s+inflation|inflation)\b.*?\b(?:is|was|are)?\s*(?:projected\s+to\s+grow\s+at|projected\s+at|grew\s+by|expanded\s+by|stood\s+at|averaged)?\s*([0-9]+(?:\.[0-9]+)?\s*(?:%|percent|per\s*cent))',
                sent_clean,
                re.IGNORECASE
            )
            if macro_match:
                attr = macro_match.group(1).strip()
                val = re.sub(r'per\s*cent|percent', '%', macro_match.group(2), flags=re.IGNORECASE).strip()
                pred = "gdp_growth_rate" if "gdp" in attr.lower() or "growth" in attr.lower() else "inflation_rate"
                facts.append({
                    "subject": "India Economy",
                    "predicate": pred,
                    "object_value": val,
                    "value_type": "percentage",
                    "temporal_context": sent_temporal,
                    "scope_context": scope,
                    "geographic_context": "India",
                    "confidence": 0.94,
                    "evidence_text": sent_clean
                })

            # 5. Pincode Reach & Network patterns
            pincode_match = re.search(
                r'(?:covered|serviced|reach of|network across)\s*([0-9]+(?:,[0-9]+)?)\s*pin\s*codes?',
                sent_clean,
                re.IGNORECASE
            )
            if pincode_match:
                val = pincode_match.group(1).strip() + " pin codes"
                facts.append({
                    "subject": default_entity,
                    "predicate": "pincode_reach",
                    "object_value": val,
                    "value_type": "number",
                    "temporal_context": sent_temporal,
                    "scope_context": scope,
                    "geographic_context": "India",
                    "confidence": 0.92,
                    "evidence_text": sent_clean
                })


        return facts

    def compare_facts(self, fact_a: Dict[str, Any], fact_b: Dict[str, Any]) -> Dict[str, Any]:
        # Fallback will delegate to deterministic comparators in comparison service
        return {
            "relationship_type": "UNCERTAIN",
            "confidence": 0.5,
            "reasoning": "Fallback comparison deferred to rule-based engine.",
            "context_explanation": None
        }


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.fallback = FallbackRuleBasedProvider()

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[Dict[str, Any]]:
        """Call Gemini REST API with JSON response format."""
        if not self.api_key:
            return None

        # Standard Gemini generateContent endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_instruction}
                ]
            },
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
            else:
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.warning(f"Error calling Gemini API: {e}. Falling back to deterministic heuristics.")
            return None

    def extract_facts(self, chunk_text: str, page_number: int, document_name: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            return self.fallback.extract_facts(chunk_text, page_number, document_name)

        user_prompt = f"""Document: {document_name}
Page: {page_number}
Passage Content:
\"\"\"
{chunk_text}
\"\"\"
Extract all factual, grounded claims following the requested JSON schema."""

        result = self._call_gemini_api(user_prompt, FACT_EXTRACTION_SYSTEM_PROMPT)
        if result and isinstance(result, dict) and "facts" in result and isinstance(result["facts"], list):
            extracted = []
            for f in result["facts"]:
                # Ensure evidence text is present in the chunk
                ev = f.get("evidence_text", "")
                if ev and (ev in chunk_text or ev.lower() in chunk_text.lower() or len(set(ev.split()).intersection(set(chunk_text.split()))) >= 4):
                    extracted.append(f)
                else:
                    # Grounding check failed - attach closest sentence from chunk
                    for sent in chunk_text.split("."):
                        if any(token.lower() in sent.lower() for token in str(f.get("object_value", "")).split() if len(token) > 2):
                            f["evidence_text"] = sent.strip()
                            extracted.append(f)
                            break
            if extracted:
                return extracted

        # If LLM returned empty or failed, run fallback to ensure high-recall grounded extraction
        fallback_facts = self.fallback.extract_facts(chunk_text, page_number, document_name)
        return fallback_facts

    def compare_facts(self, fact_a: Dict[str, Any], fact_b: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.compare_facts(fact_a, fact_b)

        user_prompt = f"""Fact A:
- Subject: {fact_a.get('subject')} (Normalized: {fact_a.get('normalized_subject')})
- Predicate: {fact_a.get('predicate')} (Normalized: {fact_a.get('normalized_predicate')})
- Value: {fact_a.get('object_value')} (Normalized: {fact_a.get('normalized_value_text')})
- Temporal Context: {fact_a.get('temporal_context')}
- Scope Context: {fact_a.get('scope_context')}
- Geographic Context: {fact_a.get('geographic_context')}
- Evidence: \"{fact_a.get('evidence_text')}\" (Page {fact_a.get('evidence_page')})

Fact B:
- Subject: {fact_b.get('subject')} (Normalized: {fact_b.get('normalized_subject')})
- Predicate: {fact_b.get('predicate')} (Normalized: {fact_b.get('normalized_predicate')})
- Value: {fact_b.get('object_value')} (Normalized: {fact_b.get('normalized_value_text')})
- Temporal Context: {fact_b.get('temporal_context')}
- Scope Context: {fact_b.get('scope_context')}
- Geographic Context: {fact_b.get('geographic_context')}
- Evidence: \"{fact_b.get('evidence_text')}\" (Page {fact_b.get('evidence_page')})

Classify their relationship strictly according to the instructions."""

        result = self._call_gemini_api(user_prompt, FACT_COMPARISON_SYSTEM_PROMPT)
        if result and isinstance(result, dict) and "relationship_type" in result:
            return result

        return self.fallback.compare_facts(fact_a, fact_b)


def get_llm_provider() -> LLMProvider:
    """Returns GeminiLLMProvider if key exists, else FallbackRuleBasedProvider."""
    if settings.GEMINI_API_KEY:
        return GeminiLLMProvider()
    return FallbackRuleBasedProvider()
