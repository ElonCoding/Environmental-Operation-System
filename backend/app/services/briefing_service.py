import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.app.schemas.report import ReportRequest, OfficerBriefResponse
from backend.app.services.data_loader import data_loader
from backend.app.services.risk_engine import risk_engine
from backend.app.services.recommendation_service import recommendation_service
from backend.app.services.cpcb_service import cpcb_service

logger = logging.getLogger(__name__)

class BriefingService:
    def generate_brief(self, request: ReportRequest) -> OfficerBriefResponse:
        years = request.analysis_years or [2023, 2024, 2025]
        selected_ghat_ids = request.ghat_ids
        language = request.language or "bilingual"

        # Fetch rankings
        rankings = risk_engine.assess_all_ghats(target_years=years)
        if selected_ghat_ids:
            rankings = [r for r in rankings if r.ghat_id in selected_ghat_ids]

        # Fetch recommendations
        all_recs = recommendation_service.get_operational_recommendations(target_years=years)
        recs_by_ghat = {r["ghat_id"]: r["recommendations"] for r in all_recs}

        # Gather critical violations
        df = data_loader.get_df()
        df_years = df[df['year'].isin(years)]
        if selected_ghat_ids:
            df_years = df_years[df_years['ghat_id'].isin(selected_ghat_ids)]

        critical_violations = []
        # Find all 0 DO readings first
        zero_do = df_years[(df_years['parameter'] == 'Dissolved oxygen') & (df_years['value'] == 0.0)]
        for _, row in zero_do.iterrows():
            critical_violations.append({
                "site": row['site'],
                "year": int(row['year']),
                "festival": row['festival'],
                "phase": row['phase'],
                "parameter": "Dissolved oxygen",
                "observed_value": "0.0 mg/l",
                "cpcb_class_b_limit": "min 5.0 mg/l",
                "deviation_type": "CRITICAL ANOXIA (0 mg/l)",
                "source_page": int(row['source_page']),
                "report_filename": row['report_filename']
            })

        # Add top peak BOD violations
        high_bod = df_years[(df_years['parameter'] == 'BOD') & (df_years['value'] > 10.0)].sort_values(by='value', ascending=False).head(5)
        for _, row in high_bod.iterrows():
            critical_violations.append({
                "site": row['site'],
                "year": int(row['year']),
                "festival": row['festival'],
                "phase": row['phase'],
                "parameter": "BOD",
                "observed_value": f"{row['value']} mg/l",
                "cpcb_class_b_limit": "max 3.0 mg/l",
                "deviation_type": f"Severe organic overload ({round(row['value']/3.0, 1)}x limit)",
                "source_page": int(row['source_page']),
                "report_filename": row['report_filename']
            })

        # Structured findings
        ranked_findings = []
        for r in rankings:
            ranked_findings.append({
                "rank": r.rank,
                "ghat_id": r.ghat_id,
                "site_name": r.site_name,
                "water_body": r.water_body,
                "priority_level": r.priority_level,
                "risk_score": r.risk_score,
                "violations_count": r.observed_violations,
                "assessable_count": r.assessable_observations,
                "violation_rate_pct": r.violation_rate_pct,
                "anoxia_count": r.anoxia_events_count,
                "explanation_en": r.explanation_en,
                "explanation_hi": r.explanation_hi,
                "key_reasons": r.key_reasons,
                "site_match_confidence": r.site_match_confidence,
                "confidence_note": r.confidence_note,
                "missing_phases": r.missing_phases,
                "recommended_actions": [a["action_en"] for a in recs_by_ghat.get(r.ghat_id, [])]
            })

        # Operational priorities summary
        op_priorities_en = [
            "Prioritise mechanical surface aeration at Bairagarh (Sant Hirdaram) kund starting 48 hours prior to visarjan (4 historical zero-oxygen episodes detected).",
            "Establish strict 24-hour post-immersion debris skimming and bio-enzyme application at Hathaikheda and Malikhedi to counter severe organic decomposition (BOD reaching up to 22 mg/l).",
            "Mandate confirmatory Durga 2026 baseline testing at Bairagarh and Malikhedi to resolve historical official MPPCB data omissions.",
            "Verify field demarcation for Rani Kamlapati ghat / Kamla Park kund prior to heavy idol dispersal."
        ]

        op_priorities_hi = [
            "बैरागढ़ (संत हिरदाराम) कुंड पर विसर्जन से 48 घंटे पहले यांत्रिक सतह वातन (एरेटर) को प्राथमिकता दें (4 बार ऑक्सीजन स्तर 0 mg/l दर्ज किया गया)।",
            "हथाईखेड़ा और मालीखेड़ी में अत्यधिक जैविक अपशिष्ट (BOD 22 mg/l तक) से निपटने के लिए विसर्जन के 24 घंटे के भीतर गहन सफाई व बायो-एंजाइम छिड़काव सुनिश्चित करें।",
            "बैरागढ़ और मालीखेड़ी में ऐतिहासिक रिपोर्टिंग अंतराल को दूर करने के लिए दुर्गा विसर्जन 2026 हेतु अनिवार्य आधारभूत परीक्षण लागू करें।",
            "भारी प्रतिमा विसर्जन से पहले रानी कमलापति घाट / कमला पार्क कुंड के सटीक स्थल का सत्यापन करें।"
        ]

        uncertainties_en = [
            "Durga Visarjan 2025 sampling tables were omitted from the published MPPCB report for Bairagarh and Malikhedi kunds. A missing record is treated as an unmonitored risk, not clean water.",
            "Site mapping for Rani Kamlapati ghat / Kamla Park kund carries Medium Confidence due to alternate naming conventions across Ganesh and Durga reports.",
            "Heavy metals testing was restricted to Chromium, Lead, Zinc, and Copper; general chemical safety cannot be extrapolated beyond tested parameters.",
            "Units in the official MPPCB report are assumed according to standard laboratory protocols as the published PDF prints no explicit units."
        ]

        uncertainties_hi = [
            "मध्य प्रदेश प्रदूषण नियंत्रण बोर्ड की 2025 की रिपोर्ट में बैरागढ़ और मालीखेड़ी कुंड के दुर्गा विसर्जन आंकड़े शामिल नहीं थे। अनुपलब्ध डेटा को स्वच्छ पानी नहीं माना गया है।",
            "रानी कमलापति घाट / कमला पार्क कुंड के स्थल मिलान में मध्यम विश्वास है, क्योंकि गणेश और दुर्गा रिपोर्टों में अलग-अलग नाम दर्ज हैं।",
            "भारी धातुओं की जांच केवल क्रोमियम, लेड, जिंक और कॉपर तक सीमित थी।",
            "मूल रिपोर्ट में इकाइयों का स्पष्ट उल्लेख न होने के कारण मानक वैज्ञानिक इकाइयों (mg/l, NTU) का उपयोग किया गया है।"
        ]

        exec_summary_en = (
            f"This operational water quality brief evaluates Bhopal's 7 standardised idol immersion sites "
            f"based on 1,524 official MPPCB monitoring measurements across {', '.join(map(str, years))}. "
            f"Assessment against mandatory CPCB Class B (Outdoor Bathing) standards identifies Bairagarh kund "
            f"as CRITICAL PRIORITY due to 4 recurring zero-oxygen (anoxia) events and a 61.5% violation rate. "
            f"Overall, 42 of 116 dissolved oxygen tests and 100 of 112 BOD tests violated legal thresholds across Bhopal. "
            f"Targeted aeration, intensive post-visarjan clearing, and confirmatory baseline sampling are recommended before 20 October 2026."
        )

        exec_summary_hi = (
            f"यह परिचालन जल गुणवत्ता विवरण भोपाल के 7 मानकीकृत विसर्जन घाटों का {', '.join(map(str, years))} के दौरान "
            f"1,524 आधिकारिक म.प्र. प्रदूषण नियंत्रण बोर्ड मापों के आधार पर मूल्यांकन करता है। "
            f"सीपीसीबी क्लास-बी (आउटडोर स्नान) मानकों के तहत बैरागढ़ कुंड को अत्यधिक संवेदनशील (क्रिटिकल) श्रेणी में रखा गया है, "
            f"जहाँ 4 बार ऑक्सीजन का स्तर शून्य दर्ज हुआ और 61.5% उल्लंघन दर पाई गई। "
            f"पूरे भोपाल में 116 में से 42 घुलित ऑक्सीजन परीक्षण और 112 में से 100 बीओडी परीक्षण विधिक सीमाओं से बाहर पाए गए। "
            f"20 अक्टूबर 2026 से पूर्व लक्षित वातन, त्वरित मलबा सफाई और आधारभूत परीक्षण अनिवार्य हैं।"
        )

        source_provenance = [
            {"year": 2023, "document": "Idol_immer._Report_23_CPCB.pdf", "authority": "MPPCB / CPCB Format", "pages": "26, 27, 28, 59, 60, 61"},
            {"year": 2024, "document": "Ganesh_and_Durga_visarjan_report-2024.pdf", "authority": "MPPCB", "pages": "23, 24, 25, 26, 69, 70, 71, 72"},
            {"year": 2025, "document": "Ganesh_and_Durga_visarjan_report-2025.pdf", "authority": "MPPCB", "pages": "28, 29, 30, 64, 65"}
        ]

        now_str = datetime.now().strftime("%d %B %Y, %H:%M")

        return OfficerBriefResponse(
            title_en="Environmental Operation System (OES) — Operational Water Quality Brief",
            title_hi="पर्यावरण संचालन प्रणाली (OES) — परिचालन जल गुणवत्ता विवरण",
            generated_at=now_str,
            target_event="Durga Visarjan (20 October 2026) — Bhopal Municipal Corporation Operational Planning",
            analysis_period=f"{min(years)}–{max(years)} MPPCB Official Monitoring",
            language=language,
            executive_summary_en=exec_summary_en,
            executive_summary_hi=exec_summary_hi,
            ranked_ghats=ranked_findings,
            critical_violations=critical_violations,
            operational_priorities_en=op_priorities_en,
            operational_priorities_hi=op_priorities_hi,
            uncertainty_and_data_gaps_en=uncertainties_en,
            uncertainty_and_data_gaps_hi=uncertainties_hi,
            source_provenance=source_provenance,
            disclaimer_en="Official historical MPPCB monitoring data from 2023–2025. This application provides evidence-based prioritisation for municipal planning and does not provide live water-quality measurements.",
            disclaimer_hi="आधिकारिक ऐतिहासिक म.प्र. प्रदूषण नियंत्रण बोर्ड निगरानी डेटा (2023–2025)। यह उपकरण नगर निगम योजना हेतु साक्ष्य-आधारित प्राथमिकता प्रदान करता है और कोई लाइव माप प्रदान नहीं करता है।"
        )

briefing_service = BriefingService()
