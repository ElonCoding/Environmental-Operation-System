import logging
from typing import List, Dict, Any, Optional
from backend.app.services.data_loader import data_loader, CANONICAL_GHATS
from backend.app.services.risk_engine import risk_engine

logger = logging.getLogger(__name__)

class RecommendationService:
    def get_operational_recommendations(
        self,
        target_years: Optional[List[int]] = None,
        ghat_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        rankings = risk_engine.assess_all_ghats(target_years=target_years)
        
        if ghat_id:
            rankings = [r for r in rankings if r.ghat_id == ghat_id]

        recommendations = []

        for r in rankings:
            site_recs = []

            # 1. Trigger: Anoxia (DO == 0)
            if r.anoxia_events_count > 0:
                site_recs.append({
                    "priority": "IMMEDIATE_ACTION",
                    "category": "Aeration & Fish-Kill Prevention",
                    "action_en": f"Deploy mechanical aeration (floating fountains / venturi aerators) at least 48 hours prior to immersion.",
                    "action_hi": f"विसर्जन से कम से कम 48 घंटे पहले यांत्रिक वातन (सतह एरेटर / फव्वारे) तैनात करें।",
                    "trigger_evidence": f"Recorded 0 mg/l dissolved oxygen (complete anoxia) across {r.anoxia_events_count} official sampling rounds.",
                    "operational_rationale": "Water at 0 mg/l dissolved oxygen cannot sustain aquatic life. Immersion organic loading accelerates total oxygen depletion into septic failure."
                })

            # 2. Trigger: Chronic DO violation (DO < 5 mg/l)
            elif r.do_violations_count > 0:
                site_recs.append({
                    "priority": "HIGH_OPERATIONAL",
                    "category": "Water Circulation & Testing",
                    "action_en": "Pre-position standby mobile aeration units and increase dissolved oxygen spot checks during immersion peak hours.",
                    "action_hi": "स्टैंडबाय मोबाइल वातन इकाइयों को तैयार रखें और विसर्जन के व्यस्त समय में घुलित ऑक्सीजन की जांच तेज करें।",
                    "trigger_evidence": f"{r.do_violations_count} dissolved oxygen readings fell below the mandatory CPCB Class B 5.0 mg/l threshold.",
                    "operational_rationale": "Sustained sub-5 mg/l dissolved oxygen indicates poor water exchange and elevated biochemical stress."
                })

            # 3. Trigger: Severe organic loading (BOD > 3 mg/l)
            if r.bod_violations_count > 0:
                site_recs.append({
                    "priority": "HIGH_OPERATIONAL",
                    "category": "Organic Sludge Skimming",
                    "action_en": "Enforce rigorous post-visarjan cleanup within 24 hours: remove floral debris, bamboo structures, and deploy bio-enzymes to accelerate organic breakdown.",
                    "action_hi": "विसर्जन के 24 घंटे के भीतर गहन सफाई सुनिश्चित करें: फूल, बांस की संरचनाएं हटाएं और बायो-एंजाइम का छिड़काव करें।",
                    "trigger_evidence": f"{r.bod_violations_count} of {r.assessable_observations} readings exceeded CPCB BOD limit (3.0 mg/l).",
                    "operational_rationale": "Decomposing festival offerings and clay binders consume dissolved oxygen rapidly, leading to prolonged post-festival water quality deterioration."
                })

            # 4. Trigger: Reporting Gaps / Missing Sampling Phases
            if len(r.missing_phases) > 0:
                site_recs.append({
                    "priority": "DATA_INTEGRITY",
                    "category": "Baseline Testing Mandate",
                    "action_en": f"Mandate formal baseline water testing for Durga Visarjan 2026 to resolve historical reporting omissions ({', '.join(r.missing_phases[:2])}).",
                    "action_hi": f"ऐतिहासिक रिपोर्टिंग अंतराल ({', '.join(r.missing_phases[:2])}) को दूर करने के लिए दुर्गा विसर्जन 2026 हेतु अनिवार्य आधारभूत नमूनाकरण लागू करें।",
                    "trigger_evidence": f"{len(r.missing_phases)} sampling phases omitted from official MPPCB reports.",
                    "operational_rationale": "A blank in the official report indicates unmonitored risk, not clean water. BMC officers require verified pre-immersion data."
                })

            # 5. Trigger: Ambiguous Site Match Confidence
            if r.site_match_confidence == "medium":
                site_recs.append({
                    "priority": "FIELD_VERIFICATION",
                    "category": "Ground Boundary Demarcation",
                    "action_en": "Conduct ground inspection to clearly demarcate the exact visarjan barrier between Kamla Park kund and Lower Lake ghat.",
                    "action_hi": "कमला पार्क कुंड और लोअर लेक घाट के बीच विसर्जन सीमा को स्पष्ट रूप से चिह्नित करने के लिए स्थल निरीक्षण करें।",
                    "trigger_evidence": "MPPCB tables switch between 'Kamla Park kund' (Ganesh) and 'Lower Lake ghat' (Durga).",
                    "operational_rationale": "Different water bodies possess drastically different dilution volumes and ecological vulnerabilities."
                })

            recommendations.append({
                "ghat_id": r.ghat_id,
                "site_name": r.site_name,
                "water_body": r.water_body,
                "priority_level": r.priority_level,
                "rank": r.rank,
                "recommendations": site_recs
            })

        return recommendations

recommendation_service = RecommendationService()
