import re
from typing import Dict, Any, Optional

class ContextExtractor:
    @staticmethod
    def extract_context(text: str) -> Dict[str, Optional[str]]:
        """
        Extracts temporal, geographic, and scope context from text chunks or sentences.
        """
        temporal = None
        geographic = None
        scope = None

        # 1. Temporal context detection
        # Fiscal years: FY2023, FY 2024, FY24, 2023-24, FY2024/25, 2025-26
        fy_match = re.search(
            r'\b(FY\s*20\d{2}(?:[/-]\d{2})?|FY\s*\d{2}|FY20\d{2}|FY\d{2}|20\d{2}[/-]\d{2}|financial year 20\d{2}[/-]\d{2})\b',
            text,
            re.IGNORECASE
        )
        if fy_match:
            temporal = fy_match.group(0).strip()
        else:
            # Quarter detection
            q_match = re.search(r'\b(Q[1-4]\s*(?:FY\s*\d{2,4})?|fourth quarter|third quarter|second quarter|first quarter)\b', text, re.IGNORECASE)
            if q_match:
                temporal = q_match.group(0).strip()
            else:
                # Standalone year
                yr_match = re.search(r'\b(20\d{2}|19\d{2})\b', text)
                if yr_match:
                    temporal = yr_match.group(0).strip()

        # 2. Scope context detection
        # Consolidated vs Standalone vs Segment
        if re.search(r'\bconsolidated\b', text, re.IGNORECASE):
            scope = "Consolidated"
        elif re.search(r'\bstandalone\b', text, re.IGNORECASE):
            scope = "Standalone"
        elif re.search(r'\bexpress parcel\b', text, re.IGNORECASE):
            scope = "Express Parcel"
        elif re.search(r'\bpart truckload|ptl\b', text, re.IGNORECASE):
            scope = "Part Truckload (PTL)"
        elif re.search(r'\bsupply chain services\b', text, re.IGNORECASE):
            scope = "Supply Chain Services"
        elif re.search(r'\btruckload\b', text, re.IGNORECASE):
            scope = "Truckload"

        # 3. Geographic context detection
        if re.search(r'\bindia\b', text, re.IGNORECASE):
            geographic = "India"
        elif re.search(r'\bglobal|international|worldwide\b', text, re.IGNORECASE):
            geographic = "Global"
        elif re.search(r'\bdelhi|gurugram|mumbai|bengaluru|indore\b', text, re.IGNORECASE):
            city_match = re.search(r'\b(delhi|gurugram|mumbai|bengaluru|indore)\b', text, re.IGNORECASE)
            if city_match:
                geographic = city_match.group(0).capitalize()

        return {
            "temporal_context": temporal,
            "geographic_context": geographic,
            "scope_context": scope
        }
