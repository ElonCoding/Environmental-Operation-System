from pydantic import BaseModel
from typing import Dict, Any

class SystemTelemetry(BaseModel):
    service_name: str = "Environmental Operation System"
    status: str = "operational"
    uptime_seconds: float
    loaded_datasets: int
    memory_usage_mb: float
    active_connections: int = 0
