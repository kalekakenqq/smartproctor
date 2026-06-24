import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from backend.database import Base, get_db
from backend.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    snapshots_dir = tmp_path / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)
    monkeypatch.setattr("backend.routers.violations.SNAPSHOTS_DIR", str(snapshots_dir))

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def register_user(client, email="user@test.com", password="password123", full_name="Test User", role="student"):
    resp = client.post("/auth/register", json={
        "email": email, "password": password, "full_name": full_name, "role": role,
    })
    return resp


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
