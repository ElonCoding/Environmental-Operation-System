import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from backend.app.services.data_loader import data_loader, CANONICAL_GHATS
from backend.app.services.cpcb_service import cpcb_service

logger = logging.getLogger(__name__)

PHASE_ORDER = {"pre": 0, "during": 1, "after": 2}

class TrendService:
    def get_ghat_timeline(
        self,
        ghat_id: str,
        parameter: str = "Dissolved oxygen"
    ) -> Dict[str, Any]:
        df = data_loader.get_df()
        site_df = df[(df['ghat_id'] == ghat_id) & (df['parameter'] == parameter)].copy()

        if len(site_df) == 0:
            return {
                "ghat_id": ghat_id,
                "parameter": parameter,
                "timeline": [],
                "cpcb_threshold": None,
                "threshold_type": None,
                "unit": "mg/l"
            }

        # Sort chronologically: year asc, festival asc, phase asc
        site_df['phase_rank'] = site_df['phase'].map(PHASE_ORDER).fillna(99)
        site_df = site_df.sort_values(by=['year', 'festival', 'phase_rank'])

        timeline_points = []
        criterion = cpcb_service.CRITERIA_CLASS_B.get(parameter)

        for _, row in site_df.iterrows():
            eval_res = cpcb_service.evaluate_reading(
                parameter=parameter,
                value=row['value'] if pd.notna(row['value']) else None,
                flag=row['flag'] if pd.notna(row['flag']) else None,
                unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
                value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None
            )

            point = {
                "record_id": row['record_id'],
                "year": int(row['year']),
                "festival": row['festival'],
                "phase": row['phase'],
                "event_label": f"{row['year']} {row['festival']} ({row['phase']})",
                "value": float(row['value']) if pd.notna(row['value']) else None,
                "value_as_printed": str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None,
                "flag": str(row['flag']) if pd.notna(row['flag']) else None,
                "unit": row['unit_assumed'],
                "status": eval_res.status,
                "is_violation": eval_res.is_violation,
                "source_page": int(row['source_page']),
                "report_filename": row['report_filename']
            }
            timeline_points.append(point)

        return {
            "ghat_id": ghat_id,
            "parameter": parameter,
            "cpcb_threshold": criterion["threshold"] if criterion and "threshold" in criterion else (criterion["min_threshold"] if criterion and "min_threshold" in criterion else None),
            "cpcb_max_threshold": criterion["max_threshold"] if criterion and "max_threshold" in criterion else None,
            "threshold_type": criterion["type"] if criterion else None,
            "unit": site_df['unit_assumed'].iloc[0] if len(site_df) > 0 and pd.notna(site_df['unit_assumed'].iloc[0]) else "mg/l",
            "timeline": timeline_points
        }

    def get_phase_impact_comparison(
        self,
        ghat_id: str,
        parameter: str = "Dissolved oxygen"
    ) -> Dict[str, Any]:
        df = data_loader.get_df()
        site_df = df[(df['ghat_id'] == ghat_id) & (df['parameter'] == parameter)]

        phase_stats = {}
        for phase in ["pre", "during", "after"]:
            sub = site_df[site_df['phase'] == phase]
            valid_vals = sub['value'].dropna().tolist()
            phase_stats[phase] = {
                "count": len(sub),
                "valid_count": len(valid_vals),
                "mean": round(sum(valid_vals) / len(valid_vals), 2) if valid_vals else None,
                "min": min(valid_vals) if valid_vals else None,
                "max": max(valid_vals) if valid_vals else None,
                "flags": sub['flag'].dropna().unique().tolist()
            }

        return {
            "ghat_id": ghat_id,
            "parameter": parameter,
            "phase_statistics": phase_stats
        }

    def get_ghat_parameters_matrix(self, ghat_id: str) -> List[Dict[str, Any]]:
        df = data_loader.get_df()
        site_df = df[df['ghat_id'] == ghat_id]

        matrix = []
        for param in sorted(site_df['parameter'].unique()):
            sub = site_df[site_df['parameter'] == param]
            valid_vals = sub['value'].dropna().tolist()
            criterion = cpcb_service.CRITERIA_CLASS_B.get(param)

            violations_count = 0
            for val in valid_vals:
                eval_res = cpcb_service.evaluate_reading(param, val)
                if eval_res.is_violation:
                    violations_count += 1

            matrix.append({
                "parameter": param,
                "unit": sub['unit_assumed'].iloc[0] if pd.notna(sub['unit_assumed'].iloc[0]) else "none",
                "total_readings": len(sub),
                "valid_numeric_readings": len(valid_vals),
                "mean_value": round(sum(valid_vals) / len(valid_vals), 2) if valid_vals else None,
                "min_value": min(valid_vals) if valid_vals else None,
                "max_value": max(valid_vals) if valid_vals else None,
                "cpcb_class_b_limit": criterion["description"] if criterion else "No applicable Class B limit",
                "violations_count": violations_count,
                "has_criteria": criterion is not None,
                "flags_observed": [str(f) for f in sub['flag'].dropna().unique()]
            })

        return matrix

trend_service = TrendService()
