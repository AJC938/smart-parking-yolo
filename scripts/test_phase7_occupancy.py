"""Phase 6-7 milestone: parking spaces + occupancy engine, end to end.

Run directly: python tests/test_phase7_occupancy.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config
from src.tracking.tracker import VehicleTracker
from src.parking.space import load_parking_spaces
from src.parking.occupancy import OccupancyEngine
from src.utils.video_io import VideoReader, VideoWriter
from src.utils.drawing import draw_detection_box, draw_hud
from src.utils.parking_drawing import draw_parking_space


def main():
    reader = VideoReader(config.VIDEO_PATH)
    tracker = VehicleTracker()
    spaces = load_parking_spaces(config.PARKING_SPACES_PATH)
    engine = OccupancyEngine()

    out_path = config.OUTPUT_DIR / "phase7_occupancy_test.mp4"
    writer = VideoWriter(out_path, reader.width, reader.height, reader.fps)

    frame_idx = 0
    start = time.time()
    last_stats = None

    for frame in reader:
        frame_idx += 1
        tracks = tracker.update(frame)
        stats = engine.update(spaces, tracks)
        last_stats = stats

        for space in spaces:
            draw_parking_space(frame, space)
        for t in tracks:
            draw_detection_box(frame, t.x1, t.y1, t.x2, t.y2, f"ID {t.track_id}")

        draw_hud(frame, [
            f"Frame {frame_idx}/{reader.frame_count}",
            f"Total: {stats.total_spaces}  Occupied: {stats.occupied_spaces}  Available: {stats.available_spaces}",
            f"Occupancy: {stats.occupancy_rate:.1f}%",
        ])
        writer.write(frame)

        if frame_idx % 50 == 0:
            print(f"  [frame {frame_idx}] occupied={stats.occupied_spaces} available={stats.available_spaces} rate={stats.occupancy_rate:.1f}%")

    writer.release()
    elapsed = time.time() - start
    print(f"Processed {frame_idx} frames in {elapsed:.1f}s ({frame_idx/elapsed:.1f} avg fps)")
    print(f"Final stats: total={last_stats.total_spaces} occupied={last_stats.occupied_spaces} "
          f"available={last_stats.available_spaces} rate={last_stats.occupancy_rate:.1f}%")
    for space in spaces:
        print(f"  {space.id}: {'OCCUPIED' if space.occupied else 'AVAILABLE'} (vehicle track {space.vehicle_track_id})")
    print(f"Annotated video saved to: {out_path}")


if __name__ == "__main__":
    main()
