"""Phase 5 milestone: detections gain persistent track IDs across frames.

Run directly: python tests/test_phase5_tracking.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config
from src.tracking.tracker import VehicleTracker
from src.utils.video_io import VideoReader, VideoWriter
from src.utils.drawing import draw_detection_box, draw_hud


def main():
    reader = VideoReader(config.VIDEO_PATH)
    tracker = VehicleTracker()

    out_path = config.OUTPUT_DIR / "phase5_tracking_test.mp4"
    writer = VideoWriter(out_path, reader.width, reader.height, reader.fps)

    frame_idx = 0
    unique_ids = set()

    for frame in reader:
        frame_idx += 1
        tracks = tracker.update(frame)

        for t in tracks:
            unique_ids.add(t.track_id)
            label = f"ID {t.track_id}"
            draw_detection_box(frame, t.x1, t.y1, t.x2, t.y2, label)

        draw_hud(frame, [
            f"Frame {frame_idx}/{reader.frame_count}",
            f"Tracked vehicles: {len(tracks)}",
            f"Unique IDs so far: {len(unique_ids)}",
        ])
        writer.write(frame)

    writer.release()
    print(f"Processed {frame_idx} frames")
    print(f"Total unique track IDs assigned: {len(unique_ids)} -> {sorted(unique_ids)}")
    print(f"Annotated video saved to: {out_path}")


if __name__ == "__main__":
    main()
