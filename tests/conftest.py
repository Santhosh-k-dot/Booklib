import sys
import os
import pytest
from fastapi.testclient import TestClient

# 🔥 ADD PROJECT ROOT TO PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from app.main import app
from app.cache import init_cache


@pytest.fixture(scope="session")
def client():
    init_cache(testing=True)   # in-memory cache for tests
    return TestClient(app)