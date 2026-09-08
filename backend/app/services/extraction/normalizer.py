import re
from typing import Optional, Tuple, Dict

# Multiplier table for standard financial and scale units
SCALE_MULTIPLIERS = {
    "crore": 10_000_000.0,
    "cr": 10_000_000.0,
    "crores": 10_000_000.0,
    "lakh": 100_000.0,
    "lacs": 100_000.0,
    "lakhs": 100_000.0,
    "lac": 100_000.0,
    "million": 1_000_000.0,
    "millions": 1_000_000.0,
    "mn": 1_000_000.0,
    "m": 1_000_000.0,
    "billion": 1_000_000_000.0,
    "billions": 1_000_000_000.0,
    "bn": 1_000_000_000.0,
    "b": 1_000_000_000.0,
    "trillion": 1_000_000_000_000.0,
    "thousand": 1_000.0,
    "k": 1_000.0,
}

WORD_TO_DIGIT = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100
}

def parse_words_to_number(text: str) -> Optional[float]:
    """Parse phrases like 'one hundred crore' or 'fifty five' into numbers."""
    tokens = text.lower().replace("-", " ").split()
    total = 0.0
    current = 0.0
    found_any = False

    for token in tokens:
        if token in WORD_TO_DIGIT:
            found_any = True
            val = WORD_TO_DIGIT[token]
            if val == 100:
                current = (current if current != 0 else 1) * 100
            else:
                current += val
        elif token in SCALE_MULTIPLIERS:
            found_any = True
            scale = SCALE_MULTIPLIERS[token]
            if current == 0:
                current = 1
            total += current * scale
            current = 0.0

    total += current
    return total if found_any and total > 0 else None


class FactNormalizer:
    @staticmethod
    def normalize_entity(entity: str) -> str:
        """Canonicalize entity/subject names."""
        if not entity:
            return "unknown_entity"
        cleaned = entity.lower().strip()
        # Remove punctuation
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        # Remove common corporate suffixes
        cleaned = re.sub(r'\b(limited|ltd|pvt|private|inc|incorporated|corp|corporation|llc|co)\b', '', cleaned)
        # Clean whitespace
        cleaned = re.sub(r'\s+', '_', cleaned.strip())

        # Canonical aliases
        aliases: Dict[str, str] = {
            "delhivery": "delhivery",
            "delhivery_express": "delhivery",
            "rbi": "reserve_bank_of_india",
            "reserve_bank": "reserve_bank_of_india",
            "reserve_bank_of_india": "reserve_bank_of_india",
            "imf": "international_monetary_fund",
            "international_monetary_fund": "international_monetary_fund",
            "goi": "government_of_india",
            "govt_of_india": "government_of_india",
            "indian_economy": "india_macroeconomy",
            "india": "india_macroeconomy",
        }
        return aliases.get(cleaned, cleaned)

    @staticmethod
    def normalize_predicate(predicate: str) -> str:
        """Canonicalize predicate/attribute names."""
        if not predicate:
            return "unknown_predicate"
        cleaned = predicate.lower().strip()
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Semantic canonicalization mapping
        if any(w in cleaned for w in ["revenue", "turnover", "sales", "generated"]):
            return "revenue"
        if any(w in cleaned for w in ["ceo", "chief executive", "managing director"]):
            return "chief_executive_officer"
        if any(w in cleaned for w in ["employee", "headcount", "workforce", "staff", "team size"]):
            return "employee_count"
        if any(w in cleaned for w in ["ebitda", "operating profit"]):
            return "ebitda"
        if any(w in cleaned for w in ["net profit", "pat", "profit after tax", "net income", "loss"]):
            return "net_profit"
        if any(w in cleaned for w in ["gdp", "growth rate", "real gdp"]):
            return "gdp_growth_rate"
        if any(w in cleaned for w in ["inflation", "cpi", "consumer price"]):
            return "inflation_rate"
        if any(w in cleaned for w in ["headquarters", "registered office", "head office", "location"]):
            return "headquarters_location"
        if any(w in cleaned for w in ["pincode", "reach", "coverage", "pin code"]):
            return "pincode_reach"
        if any(w in cleaned for w in ["shipment", "volume", "express package", "express parcel"]):
            return "shipment_volume"

        return re.sub(r'\s+', '_', cleaned)

    @staticmethod
    def normalize_value(value_str: str, value_type: str = "text") -> Tuple[Optional[float], Optional[str], Optional[str], Optional[str]]:
        """
        Normalizes a value string into:
        (canonical_float, normalized_text, unit, currency)
        Examples:
        - "₹100 crore" -> (1_000_000_000.0, "1000000000.0", "crore", "INR")
        - "one hundred crore rupees" -> (1_000_000_000.0, "1000000000.0", "crore", "INR")
        - "1,000 million" -> (1_000_000_000.0, "1000000000.0", "million", None)
        - "500 employees" -> (500.0, "500.0", "employees", None)
        - "700" -> (700.0, "700.0", None, None)
        - "6.5%" -> (6.5, "6.5%", "percent", None)
        """
        if not value_str:
            return None, "", None, None

        raw = value_str.strip()
        currency = None
        unit = None
        norm_val = None

        # Detect currency
        if "₹" in raw or "rs" in raw.lower() or "inr" in raw.lower() or "rupee" in raw.lower():
            currency = "INR"
        elif "$" in raw or "usd" in raw.lower() or "dollar" in raw.lower():
            currency = "USD"
        elif "€" in raw or "eur" in raw.lower():
            currency = "EUR"

        # Detect percentage
        if "%" in raw or "percent" in raw.lower():
            unit = "percent"
            match = re.search(r'[-+]?[0-9]*\.?[0-9]+', raw.replace(",", ""))
            if match:
                try:
                    norm_val = float(match.group())
                    return norm_val, f"{norm_val}%", unit, currency
                except ValueError:
                    pass

        # Try word-to-number parsing (e.g., "one hundred crore") only when no digits present
        if not any(c.isdigit() for c in raw):
            word_num = parse_words_to_number(raw)
            if word_num is not None:
                norm_val = word_num
                # Check unit
                for scale_word in SCALE_MULTIPLIERS:
                    if scale_word in raw.lower():
                        unit = scale_word
                        break
                return norm_val, str(norm_val), unit, currency

        # Extract numerical token and any following scale word
        # Matches: "100 crore", "1,000 million", "500", "700", "₹10,000"
        num_pattern = re.search(
            r'([₹$€]?)\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*([a-zA-Z]*)',
            raw
        )

        if num_pattern:
            curr_sym, num_str, scale_str = num_pattern.groups()
            clean_num = float(num_str.replace(",", ""))
            scale_str_lower = scale_str.lower().strip()

            if scale_str_lower in SCALE_MULTIPLIERS:
                multiplier = SCALE_MULTIPLIERS[scale_str_lower]
                norm_val = clean_num * multiplier
                unit = scale_str_lower
            else:
                norm_val = clean_num
                if scale_str_lower:
                    unit = scale_str_lower

            return norm_val, str(norm_val), unit, currency

        # Non-numerical fact
        return None, raw.strip(), unit, currency

    @staticmethod
    def normalize_temporal(temporal: Optional[str]) -> Optional[str]:
        """Normalizes temporal representations like FY23, FY 2023, 2024, Q4 FY24."""
        if not temporal:
            return None
        t = temporal.strip()
        t_clean = re.sub(r'\s+', ' ', t).upper()

        # Quarter + FY: "Q4 FY24", "Q4 FY 2024", "4TH QUARTER FY24"
        q_match = re.search(r'(Q[1-4]|QUARTER [1-4])\s*(?:OF\s*)?(?:FY|FISCAL YEAR|FINANCIAL YEAR)?\s*([0-9]{2,4})', t_clean)
        if q_match:
            q_part = q_match.group(1).replace("QUARTER ", "Q")
            year_part = q_match.group(2)
            if len(year_part) == 2:
                year_part = "20" + year_part
            return f"{q_part}_FY{year_part}"

        # Fiscal Year with range: "2024-25", "2025-26", "FY2024/25", "FY2025/26", "FY 2024-25"
        range_match = re.search(r'(?:FY)?\s*(?:20)?(\d{2})[/-](\d{2})\b', t_clean)
        if range_match:
            end_2d = range_match.group(2)
            return f"FY20{end_2d}"

        # Single Fiscal Year: "FY2023", "FY 2023", "FY23"
        fy_match = re.search(r'(?:FY|FISCAL|FINANCIAL YEAR)\s*([0-9]{2,4})', t_clean)
        if fy_match:
            start_yr = fy_match.group(1)
            if len(start_yr) == 2:
                return f"FY20{start_yr}"
            return f"FY{start_yr}"

        # Plain 4-digit calendar year: "2023", "2024"
        yr_match = re.search(r'\b(19\d{2}|20\d{2})\b', t_clean)
        if yr_match:
            return yr_match.group(1)

        return t.strip()
