import sys
import os
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from app.main import app
from app.cache import init_cache
from app.auth import get_current_user, get_current_admin
from app.database import get_db, SessionLocal
from app.models import User, UserRole, Transaction, Book


# -------------------------
# fake users for tests
# -------------------------

def fake_user():
    u = User()
    u.id = 1
    u.username = "testuser"
    u.email = "test@example.com"
    u.is_active = True
    u.role = UserRole.USER
    return u


def fake_admin():
    u = User()
    u.id = 99
    u.username = "admin"
    u.email = "admin@example.com"
    u.is_active = True
    u.role = UserRole.ADMIN
    return u


# -------------------------
# override dependencies
# -------------------------

app.dependency_overrides[get_current_user] = lambda: fake_user()
app.dependency_overrides[get_current_admin] = lambda: fake_admin()


@pytest.fixture(scope="session")
def client():
    init_cache(testing=True)

    # ✅ clean tables used in integration tests
    db = SessionLocal()
    db.query(Transaction).delete()
    db.query(Book).delete()
    db.commit()
    db.close()

    return TestClient(app)
