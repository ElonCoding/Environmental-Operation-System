from pydantic import BaseModel
from typing import Optional
from backend.app.schemas.criteria import ComparisonResult

class Reading(BaseModel):
    record_id: str
    year: int
    festival: str
    site: str
    ghat_id: str
    water_body: str
    phase: str  # pre, during, after
    parameter: str
    value: Optional[float] = None
    unit_assumed: Optional[str] = None
    flag: Optional[str] = None
    value_as_printed: Optional[str] = None
    parameter_as_printed: Optional[str] = None
    site_as_printed: Optional[str] = None
    site_match_confidence: str
    source_page: int
    report_filename: str
    comparison: ComparisonResult
