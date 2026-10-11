from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ReportRequest(BaseModel):
    analysis_years: Optional[List[int]] = None
    ghat_ids: Optional[List[str]] = None
    language: str = "bilingual"  # "en", "hi", "bilingual"
    include_recommendations: bool = True

class OfficerBriefResponse(BaseModel):
    title_en: str
    title_hi: str
    generated_at: str
    target_event: str
    analysis_period: str
    language: str
    executive_summary_en: Optional[str] = None
    executive_summary_hi: Optional[str] = None
    ranked_ghats: List[Dict[str, Any]]
    critical_violations: List[Dict[str, Any]]
    operational_priorities_en: List[str]
    operational_priorities_hi: List[str]
    uncertainty_and_data_gaps_en: List[str]
    uncertainty_and_data_gaps_hi: List[str]
    source_provenance: List[Dict[str, Any]]
    disclaimer_en: str
    disclaimer_hi: str
