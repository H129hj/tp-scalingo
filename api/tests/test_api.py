import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only-0123456789")
os.environ.setdefault("DATABASE_URL", "postgresql://app:app@localhost:5432/app")

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_notes_require_auth(client):
    assert client.get("/notes").status_code == 401


def test_full_flow(client):
    email = f"{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/auth/register", json={"email": email, "password": "motdepasse123"})
    assert r.status_code == 201
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.post("/auth/login", json={"email": email, "password": "mauvais-mdp-1"}).status_code == 401
    n = client.post("/notes", json={"title": "Premiere note", "body": "ok"}, headers=h)
    assert n.status_code == 201
    assert [x["title"] for x in client.get("/notes", headers=h).json()] == ["Premiere note"]
    assert client.delete(f"/notes/{n.json()['id']}", headers=h).status_code == 204
    assert client.get("/notes", headers=h).json() == []
