from backend.app.services.water_index import calculate_wqi

def test_pristine_water_wqi():
    score = calculate_wqi(do=7.5, bod=1.5, ph=7.4)
    assert score >= 80.0

def test_polluted_water_wqi():
    score = calculate_wqi(do=2.5, bod=12.0, ph=8.9)
    assert score < 50.0
