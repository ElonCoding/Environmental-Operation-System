import io
import csv
from typing import Optional, List
import pandas as pd

from backend.app.services.data_loader import data_loader
from backend.app.services.cpcb_service import cpcb_service

class ExportService:
    def export_evidence_csv(
        self,
        ghat_id: Optional[str] = None,
        year: Optional[int] = None,
        festival: Optional[str] = None,
        phase: Optional[str] = None,
        parameter: Optional[str] = None,
        violation_only: Optional[bool] = None
    ) -> str:
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

        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "record_id",
            "year",
            "festival",
            "site",
            "water_body",
            "phase",
            "parameter",
            "numeric_value",
            "unit_assumed",
            "flag",
            "value_as_printed",
            "parameter_as_printed",
            "site_as_printed",
            "site_match_confidence",
            "source_page",
            "report_filename",
            "cpcb_class",
            "cpcb_criterion",
            "comparison_status",
            "is_violation",
            "severity_ratio"
        ]
        writer.writerow(headers)

        for _, row in df.iterrows():
            eval_res = cpcb_service.evaluate_reading(
                parameter=row['parameter'],
                value=row['value'] if pd.notna(row['value']) else None,
                flag=row['flag'] if pd.notna(row['flag']) else None,
                unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
                value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None
            )

            if violation_only is True and not eval_res.is_violation:
                continue
            if violation_only is False and eval_res.is_violation:
                continue

            writer.writerow([
                row['record_id'],
                row['year'],
                row['festival'],
                row['site'],
                row['water_body'],
                row['phase'],
                row['parameter'],
                row['value'] if pd.notna(row['value']) else "",
                row['unit_assumed'] if pd.notna(row['unit_assumed']) else "",
                row['flag'] if pd.notna(row['flag']) else "",
                row['value_as_printed'] if pd.notna(row['value_as_printed']) else "",
                row['parameter_as_printed'] if pd.notna(row['parameter_as_printed']) else "",
                row['site_as_printed'] if pd.notna(row['site_as_printed']) else "",
                row['site_match_confidence'],
                row['source_page'],
                row['report_filename'],
                eval_res.cpcb_class,
                eval_res.limit_description,
                eval_res.status,
                eval_res.is_violation,
                eval_res.severity_ratio
            ])

        return output.getvalue()

export_service = ExportService()
