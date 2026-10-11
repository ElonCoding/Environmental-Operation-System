from pydantic import BaseModel
from typing import Optional, List

class GhatMetadata(BaseModel):
    id: str
    name: str
    water_body: str
    site_match_confidence: str  # "high" or "medium"
    confidence_note: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coordinate_source: Optional[str] = None
    is_approximate_coord: bool = True
    water_body_type: str
    historical_notes: Optional[str] = None
    available_years: List[int] = []
    total_records: int = 0
