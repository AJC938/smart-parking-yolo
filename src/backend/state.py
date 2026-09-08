"""Thread-safe in-memory application state.

The CV pipeline (running on a background thread) writes into this after
every frame; the GUI and the FastAPI layer both just read snapshots of it.
This is the "backend" from the architecture diagram -- deliberately just a
guarded in-memory object, since a database/cloud service would be pure
over-engineering for a single local monitoring app.
"""
import threading
import time
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SpaceStatus:
    id: str
    occupied: bool
    vehicle_track_id: int | None = None


@dataclass
class SystemStatus:
    video_ok: bool = False
    yolo_ok: bool = False
    tracking_ok: bool = False
    backend_ok: bool = False
    error_message: str = ""


@dataclass
class SnapshotState:
    frame: np.ndarray | None = None
    fps: float = 0.0
    total_spaces: int = 0
    occupied_spaces: int = 0
    available_spaces: int = 0
    occupancy_rate: float = 0.0
    spaces: list = field(default_factory=list)
    system: SystemStatus = field(default_factory=SystemStatus)
    frame_index: int = 0
    updated_at: float = 0.0


class AppState:
    """Singleton-style shared state guarded by a lock."""

    def __init__(self):
        self._lock = threading.Lock()
        self._state = SnapshotState()

    def update(self, **kwargs):
        with self._lock:
            for key, value in kwargs.items():
                setattr(self._state, key, value)
            self._state.updated_at = time.time()

    def snapshot(self) -> SnapshotState:
        with self._lock:
            # shallow copy is enough: frame/spaces are replaced wholesale, not mutated in place
            return SnapshotState(**vars(self._state))


app_state = AppState()
