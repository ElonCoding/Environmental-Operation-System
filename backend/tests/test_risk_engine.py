import pytest
import pandas as pd
from backend.app.services.risk_engine import risk_engine
from backend.app.services.data_loader import data_loader

def test_risk_prioritisation_all_ghats():
    summary = risk_engine.get_ranking_summary()
    assert summary.total_ghats_assessed == 7
    assert len(summary.ranked_ghats) == 7

    # Check that ranks 1 through 7 are assigned sequentially
    ranks = [g.rank for g in summary.ranked_ghats if g.rank is not None]
    assert ranks == [1, 2, 3, 4, 5, 6, 7]

    # Bairagarh (Sant Hirdaram) kund must be Rank 1 Critical Priority
    top_ghat = summary.ranked_ghats[0]
    assert "Bairagarh" in top_ghat.site_name
    assert top_ghat.priority_level == "Critical Priority"
    assert top_ghat.anoxia_events_count == 4
    assert top_ghat.risk_score >= 80.0

def test_deterministic_scoring():
    run1 = risk_engine.get_ranking_summary()
    run2 = risk_engine.get_ranking_summary()

    for g1, g2 in zip(run1.ranked_ghats, run2.ranked_ghats):
        assert g1.rank == g2.rank
        assert g1.risk_score == g2.risk_score
        assert g1.priority_level == g2.priority_level
        assert g1.observed_violations == g2.observed_violations

def test_explanations_are_evidence_derived():
    summary = risk_engine.get_ranking_summary()
    for g in summary.ranked_ghats:
        assert g.explanation_en is not None and len(g.explanation_en) > 20
        assert g.explanation_hi is not None and len(g.explanation_hi) > 20
        # The explanation must contain actual numbers from the assessment
        assert str(g.observed_violations) in g.explanation_en

def test_insufficient_evidence_handling():
    # Test handling of an empty dataframe for a site
    empty_df = pd.DataFrame()
    meta = {
        "id": "test-empty-site",
        "water_body": "Test Lake",
        "site_match_confidence": "high",
        "confidence_note": "Test note"
    }
    res = risk_engine._assess_single_ghat("Test Empty Site", meta, empty_df)
    assert res.priority_level == "Insufficient Evidence"
    assert res.risk_score is None
    assert res.rank is None
    assert "No monitoring data" in res.explanation_en
