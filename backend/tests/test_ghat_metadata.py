from backend.app.services.data_loader import CANONICAL_GHATS

def test_canonical_ghats_count():
    assert len(CANONICAL_GHATS) == 7

def test_canonical_ghats_coordinates():
    for name, data in CANONICAL_GHATS.items():
        assert "latitude" in data
        assert "longitude" in data
        assert 23.0 <= data["latitude"] <= 24.0
        assert 77.0 <= data["longitude"] <= 78.0
