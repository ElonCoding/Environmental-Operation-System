from typing import Optional, Dict, Any
from backend.app.schemas.criteria import ComparisonResult

class CPCBService:
    """
    CPCB Water Quality Criteria Evaluation Service.
    Standardized according to CPCB Class B (Outdoor Bathing - Organised).
    """

    CRITERIA_CLASS_B = {
        "Dissolved oxygen": {
            "type": "min",
            "threshold": 5.0,
            "unit": "mg/l",
            "description": "Dissolved oxygen: minimum 5.0 mg/l (CPCB Class B)"
        },
        "BOD": {
            "type": "max",
            "threshold": 3.0,
            "unit": "mg/l",
            "description": "BOD (5 days at 20°C): maximum 3.0 mg/l (CPCB Class B)"
        },
        "pH": {
            "type": "range",
            "min_threshold": 6.5,
            "max_threshold": 8.5,
            "unit": "none",
            "description": "pH: between 6.5 and 8.5 inclusive (CPCB Class B)"
        }
    }

    def evaluate_reading(
        self,
        parameter: str,
        value: Optional[float],
        flag: Optional[str] = None,
        unit_assumed: Optional[str] = None,
        value_as_printed: Optional[str] = None
    ) -> ComparisonResult:
        # Check if missing measurement
        flag_clean = str(flag).strip() if flag and str(flag) != 'nan' else None
        
        if flag_clean in ["not sampled", "*", "**"] or (value is None and flag_clean is None and not value_as_printed):
            return ComparisonResult(
                parameter=parameter,
                observed_value=None,
                observed_value_as_printed=value_as_printed or "not sampled",
                unit_assumed=unit_assumed,
                flag=flag_clean or "not sampled",
                cpcb_class="B",
                limit_description="Bathing criteria (Class B)",
                status="Missing measurement",
                is_violation=False,
                severity_ratio=0.0
            )

        # Check BDL / ND categorical observations
        if flag_clean in ["BDL", "ND"]:
            return ComparisonResult(
                parameter=parameter,
                observed_value=None,
                observed_value_as_printed=value_as_printed or flag_clean,
                unit_assumed=unit_assumed,
                flag=flag_clean,
                cpcb_class="B",
                limit_description="Below detection limit (categorical observation)",
                status="Not assessable",
                is_violation=False,
                severity_ratio=0.0
            )

        # Check if parameter has configured Class B criterion
        if parameter not in self.CRITERIA_CLASS_B:
            return ComparisonResult(
                parameter=parameter,
                observed_value=value,
                observed_value_as_printed=value_as_printed or (str(value) if value is not None else None),
                unit_assumed=unit_assumed,
                flag=flag_clean,
                cpcb_class="B",
                limit_description="No Class B outdoor bathing criterion configured for this parameter",
                status="No applicable criterion configured",
                is_violation=False,
                severity_ratio=0.0
            )

        if value is None:
            return ComparisonResult(
                parameter=parameter,
                observed_value=None,
                observed_value_as_printed=value_as_printed,
                unit_assumed=unit_assumed,
                flag=flag_clean,
                cpcb_class="B",
                limit_description="Value missing",
                status="Missing measurement",
                is_violation=False,
                severity_ratio=0.0
            )

        criterion = self.CRITERIA_CLASS_B[parameter]
        rule_type = criterion["type"]

        if rule_type == "min":
            threshold = criterion["threshold"]
            # DO min 5.0 mg/L
            if value >= threshold:
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Within applicable limit",
                    is_violation=False,
                    severity_ratio=0.0
                )
            else:
                # Below minimum (violation)
                # If value is 0.0, severity is 1.0 (anoxia)
                severity = (threshold - value) / threshold
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Exceeds applicable limit" if False else "Outside applicable range",
                    is_violation=True,
                    severity_ratio=round(severity, 3)
                )

        elif rule_type == "max":
            threshold = criterion["threshold"]
            # BOD max 3.0 mg/L
            if value <= threshold:
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Within applicable limit",
                    is_violation=False,
                    severity_ratio=0.0
                )
            else:
                # Exceeds maximum (violation)
                severity = (value - threshold) / threshold
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Exceeds applicable limit",
                    is_violation=True,
                    severity_ratio=round(severity, 3)
                )

        elif rule_type == "range":
            min_thresh = criterion["min_threshold"]
            max_thresh = criterion["max_threshold"]
            # pH 6.5 to 8.5 inclusive
            if min_thresh <= value <= max_thresh:
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Within applicable limit",
                    is_violation=False,
                    severity_ratio=0.0
                )
            else:
                # Outside range (violation)
                if value < min_thresh:
                    severity = (min_thresh - value) / 1.5
                else:
                    severity = (value - max_thresh) / 1.5
                return ComparisonResult(
                    parameter=parameter,
                    observed_value=value,
                    observed_value_as_printed=value_as_printed or str(value),
                    unit_assumed=unit_assumed or criterion["unit"],
                    flag=flag_clean,
                    cpcb_class="B",
                    limit_description=criterion["description"],
                    status="Outside applicable range",
                    is_violation=True,
                    severity_ratio=round(severity, 3)
                )

        return ComparisonResult(
            parameter=parameter,
            observed_value=value,
            observed_value_as_printed=value_as_printed,
            unit_assumed=unit_assumed,
            flag=flag_clean,
            cpcb_class="B",
            limit_description="Unknown rule",
            status="Not assessable",
            is_violation=False,
            severity_ratio=0.0
        )

cpcb_service = CPCBService()
