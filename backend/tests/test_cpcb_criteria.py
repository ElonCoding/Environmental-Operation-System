import pytest
from backend.app.services.cpcb_service import cpcb_service

def test_dissolved_oxygen_boundary():
    # Boundary: min 5.0 mg/l
    res_at_boundary = cpcb_service.evaluate_reading("Dissolved oxygen", 5.0)
    assert res_at_boundary.status == "Within applicable limit"
    assert res_at_boundary.is_violation is False

    res_above = cpcb_service.evaluate_reading("Dissolved oxygen", 7.8)
    assert res_above.status == "Within applicable limit"
    assert res_above.is_violation is False

    res_below = cpcb_service.evaluate_reading("Dissolved oxygen", 4.9)
    assert res_below.is_violation is True
    assert res_below.status == "Outside applicable range"
    assert res_below.severity_ratio > 0

    # Acute Anoxia: 0 mg/l
    res_zero = cpcb_service.evaluate_reading("Dissolved oxygen", 0.0)
    assert res_zero.is_violation is True
    assert res_zero.severity_ratio == 1.0

def test_bod_boundary():
    # Boundary: max 3.0 mg/l
    res_at_boundary = cpcb_service.evaluate_reading("BOD", 3.0)
    assert res_at_boundary.status == "Within applicable limit"
    assert res_at_boundary.is_violation is False

    res_below = cpcb_service.evaluate_reading("BOD", 2.4)
    assert res_below.status == "Within applicable limit"
    assert res_below.is_violation is False

    res_exceeds = cpcb_service.evaluate_reading("BOD", 3.1)
    assert res_exceeds.status == "Exceeds applicable limit"
    assert res_exceeds.is_violation is True
    assert res_exceeds.severity_ratio > 0

def test_ph_boundaries():
    # Range 6.5 to 8.5 inclusive
    assert cpcb_service.evaluate_reading("pH", 6.5).is_violation is False
    assert cpcb_service.evaluate_reading("pH", 7.0).is_violation is False
    assert cpcb_service.evaluate_reading("pH", 8.5).is_violation is False

    # Lower violation
    low_res = cpcb_service.evaluate_reading("pH", 6.4)
    assert low_res.is_violation is True
    assert low_res.status == "Outside applicable range"

    # Upper violation
    high_res = cpcb_service.evaluate_reading("pH", 8.6)
    assert high_res.is_violation is True
    assert high_res.status == "Outside applicable range"

def test_bdl_and_nd_handling():
    # BDL must remain categorical observation, never zero, never clean
    bdl_res = cpcb_service.evaluate_reading("Chromium", None, flag="BDL", value_as_printed="BDL")
    assert bdl_res.status == "Not assessable"
    assert bdl_res.is_violation is False
    assert bdl_res.observed_value is None

    nd_res = cpcb_service.evaluate_reading("Lead", None, flag="ND", value_as_printed="ND")
    assert nd_res.status == "Not assessable"
    assert nd_res.is_violation is False

def test_missing_measurements_handling():
    # Blank / not sampled is missing, NEVER clean
    not_sampled_res = cpcb_service.evaluate_reading("Dissolved oxygen", None, flag="not sampled")
    assert not_sampled_res.status == "Missing measurement"
    assert not_sampled_res.is_violation is False

    star_res = cpcb_service.evaluate_reading("BOD", None, flag="*")
    assert star_res.status == "Missing measurement"

    double_star_res = cpcb_service.evaluate_reading("pH", None, flag="**")
    assert double_star_res.status == "Missing measurement"

def test_parameters_without_class_b_limits():
    # Parameters without Class B limits must report "No applicable criterion configured"
    cod_res = cpcb_service.evaluate_reading("COD", 45.0)
    assert cod_res.status == "No applicable criterion configured"
    assert cod_res.is_violation is False

    turb_res = cpcb_service.evaluate_reading("Turbidity", 15.0)
    assert turb_res.status == "No applicable criterion configured"

    cond_res = cpcb_service.evaluate_reading("Conductivity", 500.0)
    assert cond_res.status == "No applicable criterion configured"
