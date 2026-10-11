import logging
from datetime import datetime
from typing import Optional, List
import pandas as pd
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import Response, JSONResponse

from backend.app.schemas.response import HealthResponse, MetadataResponse, DashboardSummary, ParameterSummary
from backend.app.schemas.ghat import GhatMetadata
from backend.app.schemas.risk import GhatRankingResponse, GhatRiskAssessment
from backend.app.schemas.report import ReportRequest, OfficerBriefResponse
from backend.app.services.data_loader import data_loader, CANONICAL_GHATS
from backend.app.services.cpcb_service import cpcb_service
from backend.app.services.risk_engine import risk_engine
from backend.app.services.evidence_service import evidence_service
from backend.app.services.trend_service import trend_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.briefing_service import briefing_service
from backend.app.services.export_service import export_service
from backend.app.reports.pdf_generator import pdf_generator

logger = logging.getLogger(__name__)

api_router = APIRouter()

@api_router.get("/health", response_model=HealthResponse)
def get_health():
    val = data_loader.get_validation_summary()
    return HealthResponse(
        status="healthy" if val.get("validation_passed", False) else "degraded",
        datasets_loaded=True,
        total_records=val.get("total_rows", 0),
        bhopal_dataset_path="data/bhopal_ghats_2023_2025.csv",
        cpcb_criteria_path="data/cpcb_water_quality_criteria.csv",
        validation_passed=val.get("validation_passed", False),
        validation_summary=val
    )

@api_router.get("/metadata", response_model=MetadataResponse)
def get_metadata():
    df = data_loader.get_df()
    return MetadataResponse(
        project_name="Environmental Operation System (OES)",
        tagline="Evidence to Action: Environmental Decision-Support & Water Quality Intelligence",
        version="1.0.0",
        scope="7 Standardised Bhopal Idol Immersion Ghats (2023–2025)",
        cpcb_class="CPCB Class B (Outdoor Bathing - Organised)",
        primary_user="Bhopal Municipal Corporation (BMC) Officer planning festival operations",
        planning_target_date="Before 20 October 2026 (Durga Visarjan)",
        ghats_count=len(CANONICAL_GHATS),
        parameters_count=len(df['parameter'].unique()),
        years_covered=sorted(df['year'].unique().tolist()),
        festivals_covered=sorted(df['festival'].unique().tolist()),
        disclaimer="Historical MPPCB monitoring data from 2023–2025. This application does not provide live water-quality measurements."
    )

@api_router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary():
    df = data_loader.get_df()
    ranking_res = risk_engine.get_ranking_summary()
    
    # Assessable observations across core parameters (DO, BOD, pH)
    core_params = ["Dissolved oxygen", "BOD", "pH"]
    core_df = df[df['parameter'].isin(core_params)]
    
    total_assessable = 0
    total_violations = 0
    zero_do_count = 0
    sites_with_repeats = set()

    param_summaries: List[ParameterSummary] = []

    for param in core_params:
        sub = core_df[core_df['parameter'] == param]
        param_assessable = 0
        param_violations = 0
        vals = []

        for _, row in sub.iterrows():
            eval_res = cpcb_service.evaluate_reading(
                param,
                row['value'] if pd.notna(row['value']) else None,
                row['flag'] if pd.notna(row['flag']) else None,
                row['unit_assumed'] if pd.notna(row['unit_assumed']) else None
            )
            if eval_res.status in ["Within applicable limit", "Exceeds applicable limit", "Outside applicable range"]:
                param_assessable += 1
                if row['value'] is not None and pd.notna(row['value']):
                    vals.append(float(row['value']))

                if eval_res.is_violation:
                    param_violations += 1
                    sites_with_repeats.add(row['site'])
                    if param == "Dissolved oxygen" and row['value'] == 0.0:
                        zero_do_count += 1

        total_assessable += param_assessable
        total_violations += param_violations

        criterion = cpcb_service.CRITERIA_CLASS_B.get(param)
        param_summaries.append(
            ParameterSummary(
                parameter=param,
                total_readings=len(sub),
                assessable_readings=param_assessable,
                violations_count=param_violations,
                violation_rate_pct=round((param_violations / param_assessable * 100), 1) if param_assessable > 0 else 0.0,
                min_value=min(vals) if vals else None,
                max_value=max(vals) if vals else None,
                unit="mg/l" if param != "pH" else "none",
                cpcb_limit=criterion["description"] if criterion else None
            )
        )

    # Phase breakdown
    phase_breakdown = {}
    for ph in ["pre", "during", "after"]:
        ph_df = df[df['phase'] == ph]
        core_ph = ph_df[ph_df['parameter'].isin(core_params)]
        ph_viol = 0
        ph_assess = 0
        for _, r in core_ph.iterrows():
            ev = cpcb_service.evaluate_reading(r['parameter'], r['value'], r['flag'])
            if ev.status in ["Within applicable limit", "Exceeds applicable limit", "Outside applicable range"]:
                ph_assess += 1
                if ev.is_violation:
                    ph_viol += 1
        phase_breakdown[ph] = {
            "total_records": len(ph_df),
            "assessable_observations": ph_assess,
            "violations_count": ph_viol,
            "violation_rate_pct": round((ph_viol / ph_assess * 100), 1) if ph_assess > 0 else 0.0
        }

    # Top priority ghats
    top_ghats = [
        {
            "rank": g.rank,
            "ghat_id": g.ghat_id,
            "site_name": g.site_name,
            "priority_level": g.priority_level,
            "risk_score": g.risk_score,
            "violations_count": g.observed_violations,
            "anoxia_count": g.anoxia_events_count,
            "explanation_en": g.explanation_en,
            "explanation_hi": g.explanation_hi
        }
        for g in ranking_res.ranked_ghats[:3]
    ]

    missing_count = int(df['value'].isna().sum())
    completeness_pct = round(((len(df) - missing_count) / len(df)) * 100, 1)

    return DashboardSummary(
        total_standardised_ghats=len(CANONICAL_GHATS),
        total_records=len(df),
        assessable_observations=total_assessable,
        observed_violations=total_violations,
        violation_rate_pct=round((total_violations / total_assessable * 100), 1) if total_assessable > 0 else 0.0,
        locations_with_repeated_violations=len(sites_with_repeats),
        missing_data_count=missing_count,
        data_completeness_pct=completeness_pct,
        anoxia_zero_do_events=zero_do_count,
        latest_historical_observation="2025 Durga (after immersion)",
        highest_priority_ghats=top_ghats,
        parameter_summaries=param_summaries,
        phase_breakdown=phase_breakdown,
        disclaimer="Historical MPPCB monitoring data from 2023–2025. This application does not provide live water-quality measurements."
    )

@api_router.get("/ghats", response_model=List[GhatMetadata])
def get_ghats():
    return data_loader.get_ghats_metadata()

@api_router.get("/ghats/ranking", response_model=GhatRankingResponse)
def get_ghats_ranking(
    years: Optional[List[int]] = Query(None),
    festivals: Optional[List[str]] = Query(None)
):
    return risk_engine.get_ranking_summary(target_years=years, target_festivals=festivals)

@api_router.get("/ghats/{ghat_id}")
def get_ghat_detail(ghat_id: str):
    meta = data_loader.get_ghat_by_id(ghat_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Ghat with ID '{ghat_id}' not found")
    
    # Get assessment
    rankings = risk_engine.assess_all_ghats()
    assessment = next((r for r in rankings if r.ghat_id == ghat_id), None)
    
    # Parameter matrix
    param_matrix = trend_service.get_ghat_parameters_matrix(ghat_id)
    
    # Phase comparisons for DO and BOD
    do_phase = trend_service.get_phase_impact_comparison(ghat_id, "Dissolved oxygen")
    bod_phase = trend_service.get_phase_impact_comparison(ghat_id, "BOD")
    
    # Recommendations
    recs = recommendation_service.get_operational_recommendations(ghat_id=ghat_id)

    return {
        "metadata": meta,
        "assessment": assessment,
        "parameters_matrix": param_matrix,
        "do_phase_comparison": do_phase,
        "bod_phase_comparison": bod_phase,
        "recommendations": recs[0]["recommendations"] if recs else []
    }

@api_router.get("/readings")
def get_readings(
    ghat_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    festival: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    parameter: Optional[str] = Query(None),
    violation_only: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    return evidence_service.get_readings(
        ghat_id=ghat_id,
        year=year,
        festival=festival,
        phase=phase,
        parameter=parameter,
        violation_only=violation_only,
        search=search,
        skip=skip,
        limit=limit
    )

@api_router.get("/evidence")
def get_evidence(
    ghat_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    festival: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    parameter: Optional[str] = Query(None),
    violation_only: Optional[bool] = Query(None),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    return evidence_service.get_readings(
        ghat_id=ghat_id,
        year=year,
        festival=festival,
        phase=phase,
        parameter=parameter,
        violation_only=violation_only,
        status_filter=status_filter,
        search=search,
        skip=skip,
        limit=limit
    )

@api_router.get("/evidence/provenance/{record_id}")
def get_record_provenance(record_id: str):
    prov = evidence_service.get_provenance_info(record_id)
    if not prov:
        raise HTTPException(status_code=404, detail=f"Record '{record_id}' not found")
    return prov

@api_router.get("/trends")
def get_trends(
    ghat_id: str = Query(..., description="Canonical ghat ID slug"),
    parameter: str = Query("Dissolved oxygen", description="Water quality parameter")
):
    return trend_service.get_ghat_timeline(ghat_id=ghat_id, parameter=parameter)

@api_router.get("/recommendations")
def get_recommendations(
    years: Optional[List[int]] = Query(None),
    ghat_id: Optional[str] = Query(None)
):
    return recommendation_service.get_operational_recommendations(target_years=years, ghat_id=ghat_id)

@api_router.post("/reports/preview", response_model=OfficerBriefResponse)
def preview_report(request: ReportRequest):
    return briefing_service.generate_brief(request)

@api_router.post("/reports/pdf")
def generate_pdf_report(request: ReportRequest):
    brief = briefing_service.generate_brief(request)
    pdf_bytes = pdf_generator.generate_pdf(brief)
    
    filename = f"Visarjan_Ghat_Watch_Brief_{datetime.now().strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@api_router.get("/exports/evidence.csv")
def export_evidence_csv(
    ghat_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    festival: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    parameter: Optional[str] = Query(None),
    violation_only: Optional[bool] = Query(None)
):
    csv_content = export_service.export_evidence_csv(
        ghat_id=ghat_id,
        year=year,
        festival=festival,
        phase=phase,
        parameter=parameter,
        violation_only=violation_only
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bhopal_visarjan_evidence_2023_2025.csv"}
    )
