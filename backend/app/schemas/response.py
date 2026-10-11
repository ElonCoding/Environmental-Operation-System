from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class HealthResponse(BaseModel):
    status: str
    datasets_loaded: bool
    total_records: int
    bhopal_dataset_path: str
    cpcb_criteria_path: str
    validation_passed: bool
    validation_summary: Dict[str, Any]

class MetadataResponse(BaseModel):
    project_name: str
    tagline: str
    version: str
    scope: str
    cpcb_class: str
    primary_user: str
    planning_target_date: str
    ghats_count: int
    parameters_count: int
    years_covered: List[int]
    festivals_covered: List[str]
    disclaimer: str

class ParameterSummary(BaseModel):
    parameter: str
    total_readings: int
    assessable_readings: int
    violations_count: int
    violation_rate_pct: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    cpcb_limit: Optional[str] = None

class DashboardSummary(BaseModel):
    total_standardised_ghats: int
    total_records: int
    assessable_observations: int
    observed_violations: int
    violation_rate_pct: float
    locations_with_repeated_violations: int
    missing_data_count: int
    data_completeness_pct: float
    anoxia_zero_do_events: int
    latest_historical_observation: str
    highest_priority_ghats: List[Dict[str, Any]]
    parameter_summaries: List[ParameterSummary]
    phase_breakdown: Dict[str, Dict[str, Any]]
    disclaimer: str
