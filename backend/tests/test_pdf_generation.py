import pytest
from fastapi.testclient import TestClient
from backend.app.services.briefing_service import briefing_service
from backend.app.schemas.report import ReportRequest
from backend.app.reports.pdf_generator import pdf_generator

def test_direct_pdf_generation():
    req = ReportRequest(analysis_years=[2023, 2024, 2025], language="bilingual")
    brief = briefing_service.generate_brief(req)
    pdf_bytes = pdf_generator.generate_pdf(brief)

    assert isinstance(pdf_bytes, bytes)
    # Valid PDF magic header
    assert pdf_bytes.startswith(b"%PDF-")
    # Substantial size with tables and fonts
    assert len(pdf_bytes) > 5000

def test_api_pdf_download_endpoint(client: TestClient):
    payload = {
        "analysis_years": [2023, 2024, 2025],
        "language": "bilingual"
    }
    resp = client.post("/api/v1/reports/pdf", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"%PDF-")
    assert len(resp.content) > 5000
