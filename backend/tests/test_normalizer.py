import pytest
from backend.app.services.extraction.normalizer import FactNormalizer, parse_words_to_number

def test_number_word_parsing():
    # Test word parsing
    assert parse_words_to_number("one hundred crore") == 1_000_000_000.0
    assert parse_words_to_number("fifty lakh") == 5_000_000.0
    assert parse_words_to_number("ten million") == 10_000_000.0

def test_numerical_normalization_indian_system():
    # 100 crore = 1,000,000,000
    val, text, unit, curr = FactNormalizer.normalize_value("₹100 crore")
    assert val == 1_000_000_000.0
    assert curr == "INR"
    assert unit == "crore"

    # 1,000 million = 1,000,000,000
    val_m, text_m, unit_m, curr_m = FactNormalizer.normalize_value("1,000 million")
    assert val_m == 1_000_000_000.0
    assert unit_m == "million"

    # Equivalence
    assert val == val_m

def test_percentage_normalization():
    val, text, unit, curr = FactNormalizer.normalize_value("6.5%")
    assert val == 6.5
    assert unit == "percent"

def test_entity_canonicalization():
    assert FactNormalizer.normalize_entity("Delhivery Limited") == "delhivery"
    assert FactNormalizer.normalize_entity("Reserve Bank of India") == "reserve_bank_of_india"
    assert FactNormalizer.normalize_entity("RBI") == "reserve_bank_of_india"

def test_predicate_canonicalization():
    assert FactNormalizer.normalize_predicate("Chief Executive Officer") == "chief_executive_officer"
    assert FactNormalizer.normalize_predicate("CEO") == "chief_executive_officer"
    assert FactNormalizer.normalize_predicate("Revenue from Operations") == "revenue"
    assert FactNormalizer.normalize_predicate("Total Headcount") == "employee_count"

def test_temporal_normalization():
    assert FactNormalizer.normalize_temporal("FY2023") == "FY2023"
    assert FactNormalizer.normalize_temporal("FY 2023") == "FY2023"
    assert FactNormalizer.normalize_temporal("FY23") == "FY2023"
    assert FactNormalizer.normalize_temporal("Financial Year 2022-23") == "FY2023"
    assert FactNormalizer.normalize_temporal("Q4 FY24") == "Q4_FY2024"
