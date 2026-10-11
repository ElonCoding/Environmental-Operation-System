from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GhatRiskAssessment(BaseModel):
    rank: Optional[int] = None
    ghat_id: str
    site_name: str
    water_body: str
    priority_level: str  # "Critical Priority", "High Priority", "Moderate Priority", "Low Priority", "Insufficient Evidence"
    risk_score: Optional[float] = None
    score_breakdown: Dict[str, float] = {}
    explanation_en: str
    explanation_hi: str
    total_observations: int
    assessable_observations: int
    observed_violations: int
    violation_rate_pct: float
    anoxia_events_count: int
    do_violations_count: int
    bod_violations_count: int
    ph_violations_count: int
    historical_recurrence_years: List[int] = []
    latest_observation_date: Optional[str] = None
    data_coverage_pct: float
    missing_phases: List[str] = []
    site_match_confidence: str
    confidence_note: Optional[str] = None
    key_reasons: List[str] = []
    recommended_actions: List[str] = []

class GhatRankingResponse(BaseModel):
    version: str = "v1.0-deterministic"
    criteria_used: str = "CPCB Class B Outdoor Bathing"
    evaluation_date: str
    total_ghats_assessed: int
    ranked_ghats: List[GhatRiskAssessment]
    methodology_summary: str
    disclaimer: str
