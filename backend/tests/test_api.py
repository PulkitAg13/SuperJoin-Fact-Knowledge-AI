from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "SuperJoin Fact Knowledge AI" in data["project"]
    assert data["status"] == "online"

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_summary_endpoint():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_facts" in data
    assert "corroborations" in data
    assert "contradictions" in data
    assert "reconciled_cases" in data
    assert "uncertain_cases" in data

def test_issues_endpoint():
    response = client.get("/api/issues")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
