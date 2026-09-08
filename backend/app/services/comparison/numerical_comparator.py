from typing import Optional, Dict, Any
import math

class NumericalComparator:
    @staticmethod
    def compare(
        val_a: Optional[float],
        val_b: Optional[float],
        unit_a: Optional[str] = None,
        unit_b: Optional[str] = None,
        tolerance_ratio: float = 0.02
    ) -> Dict[str, Any]:
        """
        Compares two numerical values considering unit scale and floating point tolerance.
        Returns:
            is_numerical: bool
            is_equivalent: bool
            is_conflicting: bool
            diff_ratio: float
            explanation: str
        """
        if val_a is None or val_b is None:
            return {
                "is_numerical": False,
                "is_equivalent": False,
                "is_conflicting": False,
                "diff_ratio": 0.0,
                "explanation": "One or both values are non-numerical."
            }

        # Check for zero handling
        if val_a == 0.0 and val_b == 0.0:
            return {
                "is_numerical": True,
                "is_equivalent": True,
                "is_conflicting": False,
                "diff_ratio": 0.0,
                "explanation": "Both values are exactly zero."
            }

        avg = (abs(val_a) + abs(val_b)) / 2.0
        diff = abs(val_a - val_b)
        diff_ratio = diff / avg if avg > 0 else 0.0

        if math.isclose(val_a, val_b, rel_tol=tolerance_ratio) or diff_ratio <= tolerance_ratio:
            return {
                "is_numerical": True,
                "is_equivalent": True,
                "is_conflicting": False,
                "diff_ratio": diff_ratio,
                "explanation": f"Normalized values ({val_a:,.2f} and {val_b:,.2f}) are mathematically equivalent within tolerance."
            }
        else:
            return {
                "is_numerical": True,
                "is_equivalent": False,
                "is_conflicting": True,
                "diff_ratio": diff_ratio,
                "explanation": f"Values diverge significantly: {val_a:,.2f} vs {val_b:,.2f} (difference of {diff_ratio * 100:.1f}%)."
            }
