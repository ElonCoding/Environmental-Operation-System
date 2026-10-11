from pydantic import BaseModel
from typing import Optional

class CPCBCriterion(BaseModel):
    water_class: str
    designated_best_use: str
    parameter: str
    limit_type: str  # min, max, range
    limit_value: str
    unit: Optional[str] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None

class ComparisonResult(BaseModel):
    parameter: str
    observed_value: Optional[float] = None
    observed_value_as_printed: Optional[str] = None
    unit_assumed: Optional[str] = None
    flag: Optional[str] = None
    cpcb_class: str = "B"
    limit_description: Optional[str] = None
    status: str  # "Within applicable limit", "Exceeds applicable limit", "Below applicable minimum", "Outside applicable range", "Not assessable", "Missing measurement", "No applicable criterion configured"
    is_violation: bool
    severity_ratio: float = 0.0  # 0.0 if compliant or not assessable, >0.0 if violating
