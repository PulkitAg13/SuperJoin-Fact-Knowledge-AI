import pytest
from backend.app.services.comparison.numerical_comparator import NumericalComparator

def test_exact_numerical_equality():
    res = NumericalComparator.compare(1_000_000_000.0, 1_000_000_000.0)
    assert res["is_numerical"] is True
    assert res["is_equivalent"] is True
    assert res["is_conflicting"] is False

def test_numerical_divergence():
    # 500 vs 700
    res = NumericalComparator.compare(500.0, 700.0)
    assert res["is_numerical"] is True
    assert res["is_equivalent"] is False
    assert res["is_conflicting"] is True

def test_numerical_tolerance():
    # 100.0 vs 100.5 (within 2% tolerance)
    res = NumericalComparator.compare(100.0, 100.5, tolerance_ratio=0.02)
    assert res["is_equivalent"] is True

def test_non_numerical_comparison():
    res = NumericalComparator.compare(None, 500.0)
    assert res["is_numerical"] is False
    assert res["is_equivalent"] is False
