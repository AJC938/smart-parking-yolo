"""FastAPI service layer exposing the shared AppState over HTTP.

Kept intentionally thin: the pipeline worker owns all CV/application logic
and writes into AppState; this module just serializes snapshots of it.
"""
from fastapi import FastAPI

from src.backend.state import app_state

app = FastAPI(title="Smart Parking Intelligence API")


@app.get("/api/health")
def health():
    snap = app_state.snapshot()
    return {"status": "ok" if snap.system.backend_ok else "starting"}


@app.get("/api/status")
def status():
    snap = app_state.snapshot()
    return {
        "system_status": "online" if snap.system.backend_ok and not snap.system.error_message else "error",
        "error_message": snap.system.error_message,
        "video_ok": snap.system.video_ok,
        "yolo_ok": snap.system.yolo_ok,
        "tracking_ok": snap.system.tracking_ok,
        "backend_ok": snap.system.backend_ok,
        "current_fps": round(snap.fps, 1),
        "frame_index": snap.frame_index,
        "total_spaces": snap.total_spaces,
        "occupied_spaces": snap.occupied_spaces,
        "available_spaces": snap.available_spaces,
        "occupancy_rate": round(snap.occupancy_rate, 1),
    }


@app.get("/api/parking")
def parking():
    snap = app_state.snapshot()
    return {
        "total_spaces": snap.total_spaces,
        "occupied_spaces": snap.occupied_spaces,
        "available_spaces": snap.available_spaces,
        "occupancy_rate": round(snap.occupancy_rate, 1),
        "spaces": [
            {"id": s.id, "status": "OCCUPIED" if s.occupied else "AVAILABLE", "vehicle_track_id": s.vehicle_track_id}
            for s in snap.spaces
        ],
    }
