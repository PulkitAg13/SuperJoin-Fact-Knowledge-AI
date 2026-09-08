import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models.fact import Fact
from backend.app.services.comparison.relationship_classifier import RelationshipClassifier

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_case_1_corroboration(db_session):
    """
    Case 1: Corroboration
    Doc A: 'Revenue for FY2023 was ₹100 crore'
    Doc B: 'The company generated one hundred crore rupees during FY2023' (normalized: 1,000,000,000)
    """
    fact_a = Fact(
        document_id="doc-1",
        subject="Acme Corp",
        predicate="revenue",
        object_value="₹100 crore",
        normalized_subject="acme_corp",
        normalized_predicate="revenue",
        normalized_value=1_000_000_000.0,
        normalized_value_text="1000000000.0",
        value_type="currency",
        temporal_context="FY2023",
        confidence=0.95,
        evidence_text="Revenue for FY2023 was ₹100 crore.",
        evidence_page=1
    )
    fact_b = Fact(
        document_id="doc-2",
        subject="Acme Corp",
        predicate="revenue",
        object_value="1,000 million",
        normalized_subject="acme_corp",
        normalized_predicate="revenue",
        normalized_value=1_000_000_000.0,
        normalized_value_text="1000000000.0",
        value_type="currency",
        temporal_context="FY2023",
        confidence=0.95,
        evidence_text="The company generated one thousand million in FY2023.",
        evidence_page=3
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    classifier = RelationshipClassifier(db_session)
    result = classifier.classify_pair(fact_a, fact_b)

    assert result is not None
    assert result["relationship_type"] == "CORROBORATES"
    assert "equivalent" in result["reasoning"].lower() or "normalized" in result["reasoning"].lower()

def test_case_2_genuine_contradiction(db_session):
    """
    Case 2: Genuine Contradiction
    Doc A: 'The company has 500 employees'
    Doc B: 'The company has 700 employees'
    Context is identical (same entity, same period).
    """
    fact_a = Fact(
        document_id="doc-1",
        subject="Acme Corp",
        predicate="employee_count",
        object_value="500 employees",
        normalized_subject="acme_corp",
        normalized_predicate="employee_count",
        normalized_value=500.0,
        normalized_value_text="500.0",
        value_type="number",
        temporal_context="2023",
        confidence=0.90,
        evidence_text="The company has 500 employees.",
        evidence_page=2
    )
    fact_b = Fact(
        document_id="doc-2",
        subject="Acme Corp",
        predicate="employee_count",
        object_value="700 employees",
        normalized_subject="acme_corp",
        normalized_predicate="employee_count",
        normalized_value=700.0,
        normalized_value_text="700.0",
        value_type="number",
        temporal_context="2023",
        confidence=0.90,
        evidence_text="The company has 700 employees.",
        evidence_page=5
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    classifier = RelationshipClassifier(db_session)
    result = classifier.classify_pair(fact_a, fact_b)

    assert result is not None
    assert result["relationship_type"] == "CONTRADICTS"
    assert "genuine contradiction" in result["reasoning"].lower()

def test_case_3_reconciled_by_context(db_session):
    """
    Case 3: Apparent Contradiction Reconciled by Context
    Doc A: Revenue = ₹100 crore in FY2022
    Doc B: Revenue = ₹120 crore in FY2023
    """
    fact_a = Fact(
        document_id="doc-1",
        subject="Acme Corp",
        predicate="revenue",
        object_value="₹100 crore",
        normalized_subject="acme_corp",
        normalized_predicate="revenue",
        normalized_value=1_000_000_000.0,
        normalized_value_text="1000000000.0",
        value_type="currency",
        temporal_context="FY2022",
        confidence=0.95,
        evidence_text="Revenue was ₹100 crore in FY2022.",
        evidence_page=1
    )
    fact_b = Fact(
        document_id="doc-2",
        subject="Acme Corp",
        predicate="revenue",
        object_value="₹120 crore",
        normalized_subject="acme_corp",
        normalized_predicate="revenue",
        normalized_value=1_200_000_000.0,
        normalized_value_text="1200000000.0",
        value_type="currency",
        temporal_context="FY2023",
        confidence=0.95,
        evidence_text="Revenue was ₹120 crore in FY2023.",
        evidence_page=4
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    classifier = RelationshipClassifier(db_session)
    result = classifier.classify_pair(fact_a, fact_b)

    assert result is not None
    assert result["relationship_type"] == "RECONCILED_BY_CONTEXT"
    assert "reporting_period" in result["context_explanation"] or "Temporal" in result["context_explanation"]

def test_case_4_ambiguity_uncertainty(db_session):
    """
    Case 4: Ambiguous / Low Confidence facts classified as UNCERTAIN.
    """
    fact_a = Fact(
        document_id="doc-1",
        subject="Subsidiary Unit",
        predicate="status",
        object_value="Operational restructuring pending",
        normalized_subject="subsidiary_unit",
        normalized_predicate="status",
        normalized_value=None,
        normalized_value_text="operational restructuring pending",
        confidence=0.60,  # low confidence / ambiguous
        evidence_text="The unit may undergo potential changes.",
        evidence_page=10
    )
    fact_b = Fact(
        document_id="doc-2",
        subject="Subsidiary Unit",
        predicate="status",
        object_value="Operations discontinued in regional hub",
        normalized_subject="subsidiary_unit",
        normalized_predicate="status",
        normalized_value=None,
        normalized_value_text="operations discontinued in regional hub",
        confidence=0.65,
        evidence_text="Discontinued operations reported for hub.",
        evidence_page=12
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    classifier = RelationshipClassifier(db_session)
    result = classifier.classify_pair(fact_a, fact_b)

    assert result is not None
    assert result["relationship_type"] == "UNCERTAIN"
