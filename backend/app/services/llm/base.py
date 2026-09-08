from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class LLMProvider(ABC):
    @abstractmethod
    def extract_facts(self, chunk_text: str, page_number: int, document_name: str) -> List[Dict[str, Any]]:
        """Extract structured facts with grounded evidence from text chunk."""
        pass

    @abstractmethod
    def compare_facts(
        self,
        fact_a: Dict[str, Any],
        fact_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two facts and determine their relationship (CORROBORATES, CONTRADICTS, RECONCILED_BY_CONTEXT, UNCERTAIN)."""
        pass
