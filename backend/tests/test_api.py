"""Integration tests for the REST API endpoints."""

import io
import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models.request import MedicalRequestDB, RequestStatus


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite DB for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with the overridden session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ── Health ──────────────────────────────────────────────────────────


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── POST /ingest ────────────────────────────────────────────────────


def test_ingest_txt(client: TestClient):
    """Ingest a simple .txt sample file."""
    content = (
        "Dr Sophie Martin\n"
        "Demande de scanner thoracique avec injection\n"
        "Patient : M. Jean DUPONT né le 15/03/1965\n"
        "Tél : 06 12 34 56 78\n"
        "Indication : Bilan pulmonaire\n"
    )
    resp = client.post(
        "/ingest",
        files={"file": ("sample.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["status"] in [s.value for s in RequestStatus]
    assert "request" in data
    assert data["request"]["patient"]["full_name"] is not None


def test_ingest_creates_db_record(client: TestClient, session: Session):
    """Ingested file is persisted in the database."""
    content = "IRM cerveau pour Mme Claire BERNARD née le 01/01/1980\n"
    client.post(
        "/ingest",
        files={"file": ("test.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    records = session.exec(select(MedicalRequestDB)).all()
    assert len(records) == 1
    data = json.loads(records[0].data_json)
    assert "patient" in data


def test_ingest_populates_ack(client: TestClient):
    """Ingested request has a generated ack message."""
    content = (
        "Dr Pierre Lefèvre\n"
        "Scanner abdominal sans injection\n"
        "Patient : M. Luc MOREAU\n"
    )
    resp = client.post(
        "/ingest",
        files={"file": ("ack.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    data = resp.json()
    ack = data["request"].get("ack_message_fr")
    assert ack and len(ack) > 20


# ── GET /requests ───────────────────────────────────────────────────


def test_list_requests_empty(client: TestClient):
    resp = client.get("/requests")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_requests_after_ingest(client: TestClient):
    """List endpoint returns ingested records."""
    for i in range(3):
        content = f"Scanner thoracique pour M. Patient{i} DURAND\n"
        client.post(
            "/ingest",
            files={"file": (f"s{i}.txt", io.BytesIO(content.encode()), "text/plain")},
        )
    resp = client.get("/requests")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 3
    assert all("id" in it for it in items)


def test_list_requests_filter_status(client: TestClient):
    """Filter list by status."""
    content = "Scanner thoracique pour M. Foo BAR\n"
    client.post(
        "/ingest",
        files={"file": ("f.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    # Incomplet because lots of info is missing
    resp = client.get("/requests?status=incomplet")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1


# ── GET /requests/{id} ──────────────────────────────────────────────


def test_get_request_by_id(client: TestClient):
    content = "IRM thoracique pour M. Test PATIENT\n"
    ingest_resp = client.post(
        "/ingest",
        files={"file": ("t.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    req_id = ingest_resp.json()["id"]

    resp = client.get(f"/requests/{req_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == req_id
    assert "request" in data
    assert "created_at" in data


def test_get_request_not_found(client: TestClient):
    resp = client.get("/requests/nonexistent-id")
    assert resp.status_code == 404


# ── PATCH /requests/{id} ────────────────────────────────────────────


def test_update_request_status(client: TestClient):
    """Update the status of a request."""
    content = "Scanner thoracique pour M. Update TEST\n"
    ingest_resp = client.post(
        "/ingest",
        files={"file": ("u.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    req_id = ingest_resp.json()["id"]

    resp = client.patch(
        f"/requests/{req_id}",
        json={"status": "a_valider"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "a_valider"


def test_update_request_data(client: TestClient):
    """Update the structured data of a request."""
    content = "Scanner thoracique pour M. Edit TEST\n"
    ingest_resp = client.post(
        "/ingest",
        files={"file": ("e.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    req_id = ingest_resp.json()["id"]

    # Get current data, modify patient name
    get_resp = client.get(f"/requests/{req_id}")
    req_data = get_resp.json()["request"]
    req_data["patient"]["full_name"] = "Jean-Pierre MODIFIÉ"

    resp = client.patch(
        f"/requests/{req_id}",
        json={"request": req_data},
    )
    assert resp.status_code == 200

    # Verify the change persisted
    verify = client.get(f"/requests/{req_id}")
    assert verify.json()["request"]["patient"]["full_name"] == "Jean-Pierre MODIFIÉ"


def test_update_request_not_found(client: TestClient):
    resp = client.patch(
        "/requests/nonexistent-id",
        json={"status": "complet"},
    )
    assert resp.status_code == 404


# ── POST /requests/{id}/send-ack ────────────────────────────────────


def test_send_ack(client: TestClient):
    """Mock-send acknowledgement and verify status changes to route."""
    content = "Scanner thoracique pour M. Ack TEST\n"
    ingest_resp = client.post(
        "/ingest",
        files={"file": ("a.txt", io.BytesIO(content.encode()), "text/plain")},
    )
    req_id = ingest_resp.json()["id"]

    resp = client.post(f"/requests/{req_id}/send-ack")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ack_sent"] is True
    assert data["status"] == "route"
    assert "message" in data and len(data["message"]) > 0


def test_send_ack_not_found(client: TestClient):
    resp = client.post("/requests/nonexistent-id/send-ack")
    assert resp.status_code == 404
