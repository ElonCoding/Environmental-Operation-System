import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Environmental Operation System (OES)"
    TAGLINE: str = "Evidence to Action: Environmental Decision-Support & Water Quality Intelligence"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RESOURCES_DIR: Path = BASE_DIR / "resources"
    
    # Specific files
    BHOPAL_GHATS_CSV: Path = DATA_DIR / "bhopal_ghats_2023_2025.csv"
    CPCB_CRITERIA_CSV: Path = DATA_DIR / "cpcb_water_quality_criteria.csv"
    SAMPLE_BHOPAL_CSV: Path = DATA_DIR / "sample_bhopal_2025.csv"
    STATEWIDE_CSV: Path = DATA_DIR / "mp_immersion_sites_2023_2025.csv"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Optional LLM
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

settings = Settings()
