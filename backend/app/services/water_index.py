from typing import Dict

def calculate_wqi(do: float, bod: float, ph: float) -> float:
    """
    Compute simplified Water Quality Index based on CPCB weighted weights.
    Returns 0-100 score where > 80 is pristine, < 50 is heavily polluted.
    """
    # DO score (ideal >= 6)
    do_score = min(100.0, (do / 6.0) * 100.0)
    # BOD score (ideal <= 2)
    bod_score = max(0.0, 100.0 - (bod / 10.0) * 100.0)
    # pH score (ideal ~7.5)
    ph_dev = abs(ph - 7.5)
    ph_score = max(0.0, 100.0 - (ph_dev / 2.0) * 100.0)
    
    wqi = (do_score * 0.45) + (bod_score * 0.35) + (ph_score * 0.20)
    return round(wqi, 2)
