import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root is in sys.path
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.app.main import app
from backend.app.services.data_loader import data_loader

@pytest.fixture(scope="session", autouse=True)
def initialize_data():
    data_loader.load_data()

@pytest.fixture
def client():
    return TestClient(app)
