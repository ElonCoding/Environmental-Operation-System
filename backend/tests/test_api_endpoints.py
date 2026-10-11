import pytest
from fastapi.testclient import TestClient

def test_api_health(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["total_records"] == 1524
    assert data["validation_passed"] is True

def test_api_metadata(client: TestClient):
    resp = client.get("/api/v1/metadata")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ghats_count"] == 7
    assert data["parameters_count"] == 13
    assert "2026" in data["planning_target_date"]

def test_api_dashboard_summary(client: TestClient):
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_standardised_ghats"] == 7
    assert data["total_records"] == 1524
    assert data["anoxia_zero_do_events"] == 4
    assert len(data["parameter_summaries"]) == 3
    assert len(data["highest_priority_ghats"]) == 3

def test_api_ghats_list_and_detail(client: TestClient):
    resp = client.get("/api/v1/ghats")
    assert resp.status_code == 200
    ghats = resp.json()
    assert len(ghats) == 7

    # Test single ghat detail
    ghat_id = ghats[0]["id"]
    detail_resp = client.get(f"/api/v1/ghats/{ghat_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert "metadata" in detail
    assert "assessment" in detail
    assert "parameters_matrix" in detail

def test_api_ghats_ranking(client: TestClient):
    resp = client.get("/api/v1/ghats/ranking")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_ghats_assessed"] == 7
    assert len(data["ranked_ghats"]) == 7
    assert data["ranked_ghats"][0]["rank"] == 1

def test_api_evidence_and_filters(client: TestClient):
    resp = client.get("/api/v1/evidence?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1524
    assert len(data["items"]) == 10

    # Test violation_only filter
    viol_resp = client.get("/api/v1/evidence?violation_only=true")
    assert viol_resp.status_code == 200
    viol_data = viol_resp.json()
    assert viol_data["total"] > 0
    for item in viol_data["items"]:
        assert item["comparison"]["is_violation"] is True

def test_api_trends(client: TestClient):
    resp = client.get("/api/v1/trends?ghat_id=bairagarh-sant-hirdaram-kund&parameter=Dissolved%20oxygen")
    assert resp.status_code == 200
    data = resp.json()
    assert data["parameter"] == "Dissolved oxygen"
    assert len(data["timeline"]) > 0

def test_api_report_preview(client: TestClient):
    payload = {
        "analysis_years": [2023, 2024, 2025],
        "language": "bilingual",
        "include_recommendations": True
    }
    resp = client.post("/api/v1/reports/preview", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "executive_summary_en" in data
    assert "executive_summary_hi" in data
    assert len(data["ranked_ghats"]) == 7

def test_api_evidence_csv_export(client: TestClient):
    resp = client.get("/api/v1/exports/evidence.csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "record_id,year,festival" in resp.text
