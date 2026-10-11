import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from backend.app.schemas.reading import Reading
from backend.app.services.data_loader import data_loader
from backend.app.services.cpcb_service import cpcb_service

logger = logging.getLogger(__name__)

class EvidenceService:
    def get_readings(
        self,
        ghat_id: Optional[str] = None,
        year: Optional[int] = None,
        festival: Optional[str] = None,
        phase: Optional[str] = None,
        parameter: Optional[str] = None,
        violation_only: Optional[bool] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        df = data_loader.get_df()

        if ghat_id:
            df = df[df['ghat_id'] == ghat_id]
        if year:
            df = df[df['year'] == year]
        if festival:
            df = df[df['festival'] == festival]
        if phase:
            df = df[df['phase'] == phase]
        if parameter:
            df = df[df['parameter'] == parameter]

        if search:
            query = search.lower().strip()
            df = df[
                df['site'].str.lower().str.contains(query) |
                df['parameter'].str.lower().str.contains(query) |
                df['water_body'].str.lower().str.contains(query) |
                df['value_as_printed'].fillna('').str.lower().str.contains(query) |
                df['flag'].fillna('').str.lower().str.contains(query)
            ]

        readings: List[Reading] = []
        
        for _, row in df.iterrows():
            eval_res = cpcb_service.evaluate_reading(
                parameter=row['parameter'],
                value=row['value'] if pd.notna(row['value']) else None,
                flag=row['flag'] if pd.notna(row['flag']) else None,
                unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
                value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None
            )

            # Apply violation_only filter
            if violation_only is True and not eval_res.is_violation:
                continue
            if violation_only is False and eval_res.is_violation:
                continue

            # Apply status filter
            if status_filter and eval_res.status != status_filter:
                continue

            readings.append(
                Reading(
                    record_id=row['record_id'],
                    year=int(row['year']),
                    festival=row['festival'],
                    site=row['site'],
                    ghat_id=row['ghat_id'],
                    water_body=row['water_body'],
                    phase=row['phase'],
                    parameter=row['parameter'],
                    value=float(row['value']) if pd.notna(row['value']) else None,
                    unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
                    flag=str(row['flag']) if pd.notna(row['flag']) else None,
                    value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None,
                    parameter_as_printed=str(row['parameter_as_printed']) if pd.notna(row['parameter_as_printed']) else None,
                    site_as_printed=str(row['site_as_printed']) if pd.notna(row['site_as_printed']) else None,
                    site_match_confidence=row['site_match_confidence'],
                    source_page=int(row['source_page']),
                    report_filename=row['report_filename'],
                    comparison=eval_res
                )
            )

        total_matched = len(readings)
        paginated_items = readings[skip : skip + limit]

        return {
            "total": total_matched,
            "skip": skip,
            "limit": limit,
            "items": paginated_items
        }

    def get_provenance_info(self, record_id: str) -> Optional[Dict[str, Any]]:
        df = data_loader.get_df()
        sub = df[df['record_id'] == record_id]
        if len(sub) == 0:
            return None
        row = sub.iloc[0]
        eval_res = cpcb_service.evaluate_reading(
            parameter=row['parameter'],
            value=row['value'] if pd.notna(row['value']) else None,
            flag=row['flag'] if pd.notna(row['flag']) else None,
            unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
            value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None
        )
        return {
            "record_id": row['record_id'],
            "site": row['site'],
            "site_as_printed": row['site_as_printed'],
            "year": int(row['year']),
            "festival": row['festival'],
            "phase": row['phase'],
            "parameter": row['parameter'],
            "value": float(row['value']) if pd.notna(row['value']) else None,
            "value_as_printed": str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None,
            "unit_assumed": row['unit_assumed'],
            "flag": str(row['flag']) if pd.notna(row['flag']) else None,
            "source_page": int(row['source_page']),
            "report_filename": row['report_filename'],
            "site_match_confidence": row['site_match_confidence'],
            "cpcb_comparison": eval_res.model_dump(),
            "local_pdf_path": f"resources/{row['report_filename']}"
        }

evidence_service = EvidenceService()
