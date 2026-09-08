"""Background worker that runs the CV pipeline (detect -> track -> parking
association -> occupancy) continuously and publishes results to AppState.

The source clip is short (~17s), so it loops for a continuous "live"
monitoring demo rather than processing once and stopping.
"""
import threading
import time

from config import config
from src.backend.state import AppState, SpaceStatus, SystemStatus
from src.tracking.tracker import VehicleTracker
from src.parking.space import load_parking_spaces
from src.parking.occupancy import OccupancyEngine
from src.utils.video_io import VideoReader
from src.utils.drawing import draw_detection_box
from src.utils.parking_drawing import draw_parking_space


class PipelineWorker:
    def __init__(self, state: AppState):
        self.state = state
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        system = SystemStatus()

        try:
            spaces = load_parking_spaces(config.PARKING_SPACES_PATH)
        except (FileNotFoundError, ValueError) as exc:
            system.error_message = f"Parking-space config error: {exc}"
            self.state.update(system=system)
            return

        try:
            tracker = VehicleTracker()
            system.yolo_ok = True
            system.tracking_ok = True
        except RuntimeError as exc:
            system.error_message = f"YOLO model error: {exc}"
            self.state.update(system=system)
            return

        engine = OccupancyEngine()

        try:
            reader = VideoReader(config.VIDEO_PATH)
            system.video_ok = True
        except (FileNotFoundError, IOError) as exc:
            system.error_message = f"Video error: {exc}"
            self.state.update(system=system)
            return

        system.backend_ok = True
        self.state.update(system=system)

        frame_times = []
        frame_index = 0

        while not self._stop_event.is_set():
            try:
                frame = next(reader)
            except StopIteration:
                reader = VideoReader(config.VIDEO_PATH)  # loop the clip
                for space in spaces:
                    space.occupied_streak = 0  # avoid carrying stale confidence into the new loop
                continue

            t0 = time.time()
            frame_index += 1

            tracks = tracker.update(frame)
            stats = engine.update(spaces, tracks)

            for space in spaces:
                draw_parking_space(frame, space)
            for t in tracks:
                draw_detection_box(frame, t.x1, t.y1, t.x2, t.y2, f"ID {t.track_id}")

            frame_times.append(time.time() - t0)
            if len(frame_times) > 30:
                frame_times.pop(0)
            fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0.0

            self.state.update(
                frame=frame,
                fps=fps,
                total_spaces=stats.total_spaces,
                occupied_spaces=stats.occupied_spaces,
                available_spaces=stats.available_spaces,
                occupancy_rate=stats.occupancy_rate,
                spaces=[SpaceStatus(s.id, s.occupied, s.vehicle_track_id) for s in spaces],
                frame_index=frame_index,
            )
