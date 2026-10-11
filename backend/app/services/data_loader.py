import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

from backend.app.core.config import settings
from backend.app.schemas.ghat import GhatMetadata

logger = logging.getLogger(__name__)

CANONICAL_GHATS = {
    "Bairagarh (Sant Hirdaram) kund": {
        "id": "bairagarh-sant-hirdaram-kund",
        "name": "Bairagarh (Sant Hirdaram) kund",
        "water_body": "Upper Lake",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match. Note: No Durga 2025 sampling table in the official MPPCB report.",
        "latitude": 23.2789,
        "longitude": 77.3296,
        "coordinate_source": "Survey / Public landmark coordinate (Sant Hirdaram Nagar, Upper Lake)",
        "is_approximate_coord": True,
        "water_body_type": "Kund / Upper Lake Shore",
        "historical_notes": "Durga 2025 table was omitted in the MPPCB published report. Total 15 sampling events recorded."
    },
    "Khatlapura ghat": {
        "id": "khatlapura-ghat",
        "name": "Khatlapura ghat",
        "water_body": "Lower Lake",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match across all reports. 18 sampling events recorded.",
        "latitude": 23.2458,
        "longitude": 77.3916,
        "coordinate_source": "Survey / Public landmark coordinate (Khatlapura Ghat, Chhota Talab)",
        "is_approximate_coord": True,
        "water_body_type": "Natural Lake Front (Lower Lake)",
        "historical_notes": "Traditional major immersion site on Lower Lake."
    },
    "Prempura ghat": {
        "id": "prempura-ghat",
        "name": "Prempura ghat",
        "water_body": "Upper Lake",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match across all reports. 18 sampling events recorded.",
        "latitude": 23.2211,
        "longitude": 77.3734,
        "coordinate_source": "Survey / Public landmark coordinate (Prempura Ghat, Upper Lake / Van Vihar road)",
        "is_approximate_coord": True,
        "water_body_type": "Natural Lake Front (Upper Lake)",
        "historical_notes": "Major immersion site on Upper Lake; subject to NGT lake immersion transfer orders."
    },
    "Rani Kamlapati ghat / Kamla Park kund": {
        "id": "rani-kamlapati-kamla-park",
        "name": "Rani Kamlapati ghat / Kamla Park kund",
        "water_body": "Lower Lake",
        "site_match_confidence": "medium",
        "confidence_note": "Medium confidence: Ganesh festival tables designate 'Kamla Park kund', while Durga tables designate 'Lower Lake ghat'. These may represent two geographically proximate but distinct immersion spots.",
        "latitude": 23.2480,
        "longitude": 77.3940,
        "coordinate_source": "Survey / Public landmark coordinate (Kamla Park spit between Upper and Lower Lake)",
        "is_approximate_coord": True,
        "water_body_type": "Kund / Lower Lake Marginal Area",
        "historical_notes": "Site mapping uncertainty disclosed: BMC officers should verify exact ground sampling point before operational deployment."
    },
    "Hathaikheda dam / kund": {
        "id": "hathaikheda-dam-kund",
        "name": "Hathaikheda dam / kund",
        "water_body": "Hathaikheda dam",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match across all reports. 18 sampling events recorded.",
        "latitude": 23.2609,
        "longitude": 77.4899,
        "coordinate_source": "Survey / Public landmark coordinate (Hathaikheda Dam / Kund, Eastern Bhopal)",
        "is_approximate_coord": True,
        "water_body_type": "Reservoir / Dedicated Kund",
        "historical_notes": "Eastern Bhopal immersion location on Hathaikheda reservoir system."
    },
    "Malikhedi kund": {
        "id": "malikhedi-kund",
        "name": "Malikhedi kund",
        "water_body": "Kund",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match. Note: No Durga 2025 sampling table in the official MPPCB report.",
        "latitude": 23.2750,
        "longitude": 77.4580,
        "coordinate_source": "Survey / Public landmark coordinate (Malikhedi Kund)",
        "is_approximate_coord": True,
        "water_body_type": "Dedicated Immersion Kund",
        "historical_notes": "Constructed artificial kund; Durga 2025 table missing from official MPPCB report. Total 15 events."
    },
    "Shahpura lake ghat": {
        "id": "shahpura-lake-ghat",
        "name": "Shahpura lake ghat",
        "water_body": "Shahpura Lake",
        "site_match_confidence": "high",
        "confidence_note": "High confidence match across all reports. 18 sampling events recorded.",
        "latitude": 23.2047,
        "longitude": 77.4259,
        "coordinate_source": "Survey / Public landmark coordinate (Shahpura Lake Ghat, Manisha Market area)",
        "is_approximate_coord": True,
        "water_body_type": "Urban Lake Shore (Shahpura Lake)",
        "historical_notes": "Southern Bhopal urban lake immersion ghat."
    }
}

YEAR_TO_REPORT_FILE = {
    2023: "Idol_immer._Report_23_CPCB.pdf",
    2024: "Ganesh_and_Durga_visarjan_report-2024.pdf",
    2025: "Ganesh_and_Durga_visarjan_report-2025.pdf"
}

def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

class DataLoaderService:
    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._cpcb_df: Optional[pd.DataFrame] = None
        self._validation_summary: Dict[str, Any] = {}
        self._is_loaded = False

    def load_data(self) -> None:
        if self._is_loaded and self._df is not None:
            return

        bhopal_path = settings.BHOPAL_GHATS_CSV
        cpcb_path = settings.CPCB_CRITERIA_CSV

        if not bhopal_path.exists():
            raise FileNotFoundError(f"Bhopal ghats dataset not found at: {bhopal_path}")
        if not cpcb_path.exists():
            raise FileNotFoundError(f"CPCB criteria dataset not found at: {cpcb_path}")

        df = pd.read_csv(bhopal_path)
        cpcb_df = pd.read_csv(cpcb_path)

        # Ensure correct datatypes
        df['year'] = df['year'].astype(int)
        df['source_page'] = df['source_page'].astype(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Add report filename mapping
        df['report_filename'] = df['year'].map(YEAR_TO_REPORT_FILE).fillna("Unknown_Report.pdf")

        # Map ghat slug
        ghat_slug_map = {name: meta["id"] for name, meta in CANONICAL_GHATS.items()}
        df['ghat_id'] = df['site'].map(ghat_slug_map)

        # Generate unique record ID
        df['record_id'] = [
            f"REC-{row.year}-{row.festival[:1]}-{str(row.ghat_id)[:6]}-{row.phase[:1]}-{slugify(str(row.parameter))[:5]}-{idx+1}"
            for idx, row in df.iterrows()
        ]

        self._df = df
        self._cpcb_df = cpcb_df

        # Run validation
        total_rows = len(df)
        unique_sites = df['site'].unique().tolist()
        unknown_sites = [s for s in unique_sites if s not in CANONICAL_GHATS]
        null_values = df['value'].isna().sum()
        flag_counts = df['flag'].value_counts(dropna=False).to_dict()
        flag_counts_clean = {str(k): int(v) for k, v in flag_counts.items()}

        self._validation_summary = {
            "total_rows": total_rows,
            "expected_rows": 1524,
            "rows_match_expected": total_rows == 1524,
            "unique_sites_count": len(unique_sites),
            "unknown_sites": unknown_sites,
            "years_present": sorted(df['year'].unique().tolist()),
            "festivals_present": sorted(df['festival'].unique().tolist()),
            "parameters_count": len(df['parameter'].unique()),
            "null_values_count": int(null_values),
            "flag_distribution": flag_counts_clean,
            "reports_mapped": list(YEAR_TO_REPORT_FILE.values()),
            "validation_passed": len(unknown_sites) == 0 and total_rows == 1524
        }
        self._is_loaded = True
        logger.info(f"Loaded {total_rows} rows from Bhopal ghats dataset. Validation passed: {self._validation_summary['validation_passed']}")

    def get_df(self) -> pd.DataFrame:
        if not self._is_loaded:
            self.load_data()
        return self._df.copy()

    def get_cpcb_df(self) -> pd.DataFrame:
        if not self._is_loaded:
            self.load_data()
        return self._cpcb_df.copy()

    def get_validation_summary(self) -> Dict[str, Any]:
        if not self._is_loaded:
            self.load_data()
        return self._validation_summary

    def get_ghats_metadata(self) -> List[GhatMetadata]:
        df = self.get_df()
        results = []
        for site_name, meta in CANONICAL_GHATS.items():
            sub = df[df['site'] == site_name]
            years = sorted(sub['year'].unique().tolist()) if len(sub) > 0 else []
            total = len(sub)
            results.append(
                GhatMetadata(
                    id=meta["id"],
                    name=meta["name"],
                    water_body=meta["water_body"],
                    site_match_confidence=meta["site_match_confidence"],
                    confidence_note=meta["confidence_note"],
                    latitude=meta["latitude"],
                    longitude=meta["longitude"],
                    coordinate_source=meta["coordinate_source"],
                    is_approximate_coord=meta["is_approximate_coord"],
                    water_body_type=meta["water_body_type"],
                    historical_notes=meta["historical_notes"],
                    available_years=years,
                    total_records=total
                )
            )
        return results

    def get_ghat_by_id(self, ghat_id: str) -> Optional[GhatMetadata]:
        for g in self.get_ghats_metadata():
            if g.id == ghat_id:
                return g
        return None

data_loader = DataLoaderService()
