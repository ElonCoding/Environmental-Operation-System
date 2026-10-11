import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from backend.app.schemas.risk import GhatRiskAssessment, GhatRankingResponse
from backend.app.services.data_loader import data_loader, CANONICAL_GHATS
from backend.app.services.cpcb_service import cpcb_service

logger = logging.getLogger(__name__)

class RiskPrioritisationEngine:
    VERSION = "v1.1-deterministic-evidence-based"

    def assess_all_ghats(
        self,
        target_years: Optional[List[int]] = None,
        target_festivals: Optional[List[str]] = None
    ) -> List[GhatRiskAssessment]:
        df = data_loader.get_df()

        if target_years:
            df = df[df['year'].isin(target_years)]
        if target_festivals:
            df = df[df['festival'].isin(target_festivals)]

        assessments = []

        for site_name, meta in CANONICAL_GHATS.items():
            site_df = df[df['site'] == site_name]
            assessment = self._assess_single_ghat(site_name, meta, site_df)
            assessments.append(assessment)

        # Sort by:
        # 1. Has meaningful score (insufficient evidence goes to bottom)
        # 2. Risk score descending
        # 3. Anoxia events count descending
        # 4. Total violations count descending
        assessments.sort(
            key=lambda a: (
                1 if a.risk_score is not None else 0,
                a.risk_score if a.risk_score is not None else -1,
                a.anoxia_events_count,
                a.observed_violations
            ),
            reverse=True
        )

        # Assign ranks
        current_rank = 1
        for a in assessments:
            if a.risk_score is not None:
                a.rank = current_rank
                current_rank += 1
            else:
                a.rank = None

        return assessments

    def _assess_single_ghat(
        self,
        site_name: str,
        meta: Dict[str, Any],
        site_df: pd.DataFrame
    ) -> GhatRiskAssessment:
        total_obs = len(site_df)

        if total_obs == 0:
            return GhatRiskAssessment(
                rank=None,
                ghat_id=meta["id"],
                site_name=site_name,
                water_body=meta["water_body"],
                priority_level="Insufficient Evidence",
                risk_score=None,
                score_breakdown={},
                explanation_en="No monitoring data available for this site in the selected scope.",
                explanation_hi="चयनित दायरे में इस घाट के लिए कोई निगरानी डेटा उपलब्ध नहीं है।",
                total_observations=0,
                assessable_observations=0,
                observed_violations=0,
                violation_rate_pct=0.0,
                anoxia_events_count=0,
                do_violations_count=0,
                bod_violations_count=0,
                ph_violations_count=0,
                historical_recurrence_years=[],
                latest_observation_date=None,
                data_coverage_pct=0.0,
                missing_phases=[],
                site_match_confidence=meta["site_match_confidence"],
                confidence_note=meta["confidence_note"],
                key_reasons=["No recorded observations in the provided dataset."],
                recommended_actions=["Deploy baseline water sampling prior to festival immersion."]
            )

        # Assess core CPCB parameters: DO, BOD, pH
        core_params = ["Dissolved oxygen", "BOD", "pH"]
        core_df = site_df[site_df['parameter'].isin(core_params)]

        assessable_count = 0
        observed_violations = 0
        anoxia_count = 0
        do_violations = 0
        bod_violations = 0
        ph_violations = 0

        do_severity_sum = 0.0
        bod_severity_sum = 0.0
        ph_severity_sum = 0.0

        years_with_violations = set()
        recent_violation_in_2025 = False

        for _, row in core_df.iterrows():
            eval_res = cpcb_service.evaluate_reading(
                parameter=row['parameter'],
                value=row['value'] if pd.notna(row['value']) else None,
                flag=row['flag'] if pd.notna(row['flag']) else None,
                unit_assumed=row['unit_assumed'] if pd.notna(row['unit_assumed']) else None,
                value_as_printed=str(row['value_as_printed']) if pd.notna(row['value_as_printed']) else None
            )

            # Check if assessable
            if eval_res.status in ["Within applicable limit", "Exceeds applicable limit", "Outside applicable range"]:
                assessable_count += 1

                if eval_res.is_violation:
                    observed_violations += 1
                    years_with_violations.add(int(row['year']))
                    if int(row['year']) == 2025:
                        recent_violation_in_2025 = True

                    if row['parameter'] == "Dissolved oxygen":
                        do_violations += 1
                        do_severity_sum += eval_res.severity_ratio
                        if row['value'] == 0.0:
                            anoxia_count += 1
                    elif row['parameter'] == "BOD":
                        bod_violations += 1
                        bod_severity_sum += min(eval_res.severity_ratio, 3.0)  # cap extreme BOD ratios
                    elif row['parameter'] == "pH":
                        ph_violations += 1
                        ph_severity_sum += min(eval_res.severity_ratio, 2.0)

        # Check sufficiency of evidence
        # Expected minimum assessable readings for valid score: at least 5 readings across core parameters
        if assessable_count < 5:
            return GhatRiskAssessment(
                rank=None,
                ghat_id=meta["id"],
                site_name=site_name,
                water_body=meta["water_body"],
                priority_level="Insufficient Evidence",
                risk_score=None,
                score_breakdown={},
                explanation_en=f"Insufficient assessable records ({assessable_count} readings). Cannot compute statistically defensible risk score.",
                explanation_hi=f"अपर्याप्त मूल्यांकन योग्य रिकॉर्ड ({assessable_count} रीडिंग)। साक्ष्य-आधारित जोखिम स्कोर की गणना नहीं की जा सकती।",
                total_observations=total_obs,
                assessable_observations=assessable_count,
                observed_violations=observed_violations,
                violation_rate_pct=round((observed_violations / assessable_count * 100), 1) if assessable_count > 0 else 0.0,
                anoxia_events_count=anoxia_count,
                do_violations_count=do_violations,
                bod_violations_count=bod_violations,
                ph_violations_count=ph_violations,
                historical_recurrence_years=sorted(list(years_with_violations)),
                latest_observation_date=None,
                data_coverage_pct=0.0,
                missing_phases=[],
                site_match_confidence=meta["site_match_confidence"],
                confidence_note=meta["confidence_note"],
                key_reasons=["Fewer than 5 assessable observations available."],
                recommended_actions=["Schedule comprehensive baseline sampling across pre, during, and post phases."]
            )

        # Scoring Formula (Deterministic, 0 - 100):
        # 1. DO Deficit Subscore (max 35 pts):
        # DO is the life-support metric of aquatic ecology.
        do_assessable = len(core_df[(core_df['parameter'] == 'Dissolved oxygen') & (core_df['value'].notna())])
        do_rate = (do_violations / do_assessable) if do_assessable > 0 else 0.0
        do_mean_severity = (do_severity_sum / do_violations) if do_violations > 0 else 0.0
        score_do = round(min(35.0, (do_rate * 0.6 + do_mean_severity * 0.4) * 35.0), 2)

        # 2. BOD Organic Load Subscore (max 30 pts):
        bod_assessable = len(core_df[(core_df['parameter'] == 'BOD') & (core_df['value'].notna())])
        bod_rate = (bod_violations / bod_assessable) if bod_assessable > 0 else 0.0
        bod_mean_severity = (bod_severity_sum / bod_violations) if bod_violations > 0 else 0.0
        score_bod = round(min(30.0, (bod_rate * 0.6 + (bod_mean_severity / 3.0) * 0.4) * 30.0), 2)

        # 3. Acute Ecological Stress / Anoxia Penalty (max 20 pts):
        # Zero oxygen (DO = 0) represents immediate septic conditions.
        score_anoxia = 0.0
        if anoxia_count > 0:
            score_anoxia = min(20.0, 10.0 + (anoxia_count * 2.5))
        score_anoxia = round(score_anoxia, 2)

        # 4. Historical Recurrence & Recency (max 15 pts):
        site_years = sorted(site_df['year'].unique().tolist())
        recurrence_ratio = len(years_with_violations) / len(site_years) if site_years else 0.0
        score_rec = round(recurrence_ratio * 10.0 + (5.0 if recent_violation_in_2025 else 0.0), 2)

        # Total Risk Score (0 - 100)
        raw_score = score_do + score_bod + score_anoxia + score_rec
        risk_score = round(min(100.0, max(0.0, raw_score)), 1)

        # Priority Level
        if anoxia_count >= 1 or risk_score >= 75.0:
            priority_level = "Critical Priority"
        elif risk_score >= 55.0:
            priority_level = "High Priority"
        elif risk_score >= 35.0:
            priority_level = "Moderate Priority"
        else:
            priority_level = "Low Priority"

        # Data coverage calculations
        # Expected phases: 3 years * 2 festivals * 3 phases = 18 phases
        recorded_events = site_df[['year', 'festival', 'phase']].drop_duplicates()
        events_count = len(recorded_events)
        coverage_pct = round((events_count / 18.0) * 100, 1)

        missing_phases = []
        for yr in [2023, 2024, 2025]:
            for fest in ["Ganesh", "Durga"]:
                for ph in ["pre", "during", "after"]:
                    has_ev = len(site_df[(site_df['year'] == yr) & (site_df['festival'] == fest) & (site_df['phase'] == ph)]) > 0
                    if not has_ev:
                        missing_phases.append(f"{yr} {fest} ({ph})")

        # Plain language explanations
        key_reasons = []
        if anoxia_count > 0:
            key_reasons.append(f"Recorded critical anoxia (0 mg/l DO) in {anoxia_count} official sampling rounds.")
        if do_violations > 0:
            key_reasons.append(f"{do_violations} of {do_assessable} dissolved oxygen readings fell below the CPCB Class B limit (5.0 mg/l).")
        if bod_violations > 0:
            key_reasons.append(f"{bod_violations} of {bod_assessable} BOD readings exceeded the bathing criteria limit of 3.0 mg/l.")
        if ph_violations > 0:
            key_reasons.append(f"{ph_violations} pH readings deviated outside the acceptable 6.5–8.5 range.")
        if len(years_with_violations) >= 2:
            key_reasons.append(f"Persistent threshold violations verified across {len(years_with_violations)} monitoring years ({', '.join(map(str, sorted(years_with_violations)))}).")
        if len(missing_phases) > 0:
            key_reasons.append(f"Official reporting gap: {len(missing_phases)} sampling phases omitted in MPPCB tables (e.g. Durga 2025).")

        # Bilingual Explanations
        explanation_en = (
            f"Prioritised as {priority_level} (Score: {risk_score}/100). "
            f"{'Critical zero-oxygen (anoxia) detected across multiple tests. ' if anoxia_count > 0 else ''}"
            f"Historical tests show {observed_violations} of {assessable_count} assessable core parameters violated CPCB Class B limits "
            f"({round(observed_violations/assessable_count*100, 1)}% violation rate). "
            f"Recurrence confirmed in {len(years_with_violations)} of {len(site_years)} years."
        )

        explanation_hi = (
            f"प्राथमिकता श्रेणी: {priority_level} (स्कोर: {risk_score}/100)। "
            f"{'कई परीक्षणों में ऑक्सीजन का स्तर शून्य (0 mg/l) पाया गया। ' if anoxia_count > 0 else ''}"
            f"ऐतिहासिक आंकड़ों के अनुसार {assessable_count} में से {observed_violations} माप सीपीसीबी क्लास-बी मानकों का उल्लंघन करते हैं "
            f"({round(observed_violations/assessable_count*100, 1)}% उल्लंघन दर)। "
            f"{len(site_years)} में से {len(years_with_violations)} वर्षों में निरंतर उल्लंघन दर्ज किया गया।"
        )

        # Operational Recommended Actions
        recommended_actions = []
        if anoxia_count > 0 or do_rate > 0.5:
            recommended_actions.append("Immediate pre-immersion artificial aeration: Deploy mechanical surface aerators or fountains 48 hours prior to visarjan.")
        if bod_rate > 0.7:
            recommended_actions.append("Post-visarjan bioremediation and organic sludge clearing: Intensive debris skimming within 24 hours of immersion.")
        if meta["site_match_confidence"] == "medium":
            recommended_actions.append("Ground site-mapping audit: Verify whether Kamla Park kund or Lower Lake ghat represents the active immersion boundary.")
        if len(missing_phases) > 0:
            recommended_actions.append("Mandate confirmatory baseline sampling for Durga 2026 to resolve historical reporting omissions.")

        latest_ev = site_df.sort_values(by=['year'], ascending=False).iloc[0]
        latest_date_str = f"{latest_ev['year']} {latest_ev['festival']} ({latest_ev['phase']})"

        return GhatRiskAssessment(
            rank=None,
            ghat_id=meta["id"],
            site_name=site_name,
            water_body=meta["water_body"],
            priority_level=priority_level,
            risk_score=risk_score,
            score_breakdown={
                "dissolved_oxygen_subscore": score_do,
                "bod_organic_subscore": score_bod,
                "anoxia_penalty": score_anoxia,
                "historical_recurrence_subscore": score_rec
            },
            explanation_en=explanation_en,
            explanation_hi=explanation_hi,
            total_observations=total_obs,
            assessable_observations=assessable_count,
            observed_violations=observed_violations,
            violation_rate_pct=round((observed_violations / assessable_count * 100), 1),
            anoxia_events_count=anoxia_count,
            do_violations_count=do_violations,
            bod_violations_count=bod_violations,
            ph_violations_count=ph_violations,
            historical_recurrence_years=sorted(list(years_with_violations)),
            latest_observation_date=latest_date_str,
            data_coverage_pct=coverage_pct,
            missing_phases=missing_phases,
            site_match_confidence=meta["site_match_confidence"],
            confidence_note=meta["confidence_note"],
            key_reasons=key_reasons,
            recommended_actions=recommended_actions
        )

    def get_ranking_summary(
        self,
        target_years: Optional[List[int]] = None,
        target_festivals: Optional[List[str]] = None
    ) -> GhatRankingResponse:
        ranked = self.assess_all_ghats(target_years, target_festivals)
        return GhatRankingResponse(
            version=self.VERSION,
            criteria_used="CPCB Class B Outdoor Bathing (DO >= 5.0 mg/l, BOD <= 3.0 mg/l, pH 6.5-8.5)",
            evaluation_date="2026-10-11",
            total_ghats_assessed=len(ranked),
            ranked_ghats=ranked,
            methodology_summary="Deterministic multi-criteria evaluation combining dissolved oxygen deficit, biochemical oxygen demand (BOD) excess, acute anoxic events, and multi-year recurrence.",
            disclaimer="Historical MPPCB monitoring data from 2023–2025. This application provides evidence-based prioritisation for municipal planning and does not provide live water-quality measurements."
        )

risk_engine = RiskPrioritisationEngine()
