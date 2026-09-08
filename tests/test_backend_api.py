from fastapi.testclient import TestClient

from src.backend.api import app
from src.backend.state import SpaceStatus, SystemStatus, app_state


def _seed_state():
    app_state.update(
        fps=24.3,
        total_spaces=18,
        occupied_spaces=7,
        available_spaces=11,
        occupancy_rate=38.9,
        spaces=[SpaceStatus("P01", True, 5), SpaceStatus("P02", False, None)],
        system=SystemStatus(video_ok=True, yolo_ok=True, tracking_ok=True, backend_ok=True),
    )


def test_health_endpoint_reports_ok_once_backend_is_up():
    _seed_state()
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_status_endpoint_reflects_seeded_state():
    _seed_state()
    client = TestClient(app)
    resp = client.get("/api/status")
    body = resp.json()
    assert resp.status_code == 200
    assert body["system_status"] == "online"
    assert body["total_spaces"] == 18
    assert body["occupied_spaces"] == 7
    assert body["current_fps"] == 24.3


def test_parking_endpoint_lists_space_statuses():
    _seed_state()
    client = TestClient(app)
    resp = client.get("/api/parking")
    body = resp.json()
    assert resp.status_code == 200
    assert body["total_spaces"] == 18
    ids = {s["id"]: s["status"] for s in body["spaces"]}
    assert ids["P01"] == "OCCUPIED"
    assert ids["P02"] == "AVAILABLE"


def test_status_endpoint_surfaces_error_state():
    app_state.update(system=SystemStatus(error_message="Video error: file not found"))
    client = TestClient(app)
    resp = client.get("/api/status")
    body = resp.json()
    assert body["system_status"] == "error"
    assert "Video error" in body["error_message"]
