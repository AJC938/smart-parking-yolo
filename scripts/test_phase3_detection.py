"""Phase 3 milestone: video -> YOLO -> annotated video.

Run directly: python tests/test_phase3_detection.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config
from src.detection.detector import VehicleDetector
from src.utils.video_io import VideoReader, VideoWriter
from src.utils.drawing import draw_detection_box, draw_hud


def main():
    reader = VideoReader(config.VIDEO_PATH)
    print(f"Video loaded: {reader.width}x{reader.height} @ {reader.fps:.1f}fps, {reader.frame_count} frames")

    detector = VehicleDetector()
    print(f"YOLO model loaded: {config.YOLO_MODEL_PATH}")

    out_path = config.OUTPUT_DIR / "phase3_detection_test.mp4"
    writer = VideoWriter(out_path, reader.width, reader.height, reader.fps)

    frame_idx = 0
    start_time = time.time()
    total_detections = 0

    for frame in reader:
        frame_idx += 1
        t0 = time.time()
        detections = detector.detect(frame)
        infer_time = time.time() - t0
        fps_estimate = 1.0 / infer_time if infer_time > 0 else 0.0
        total_detections += len(detections)

        for det in detections:
            label = f"{det.class_name} {det.confidence:.2f}"
            draw_detection_box(frame, det.x1, det.y1, det.x2, det.y2, label)

        draw_hud(frame, [
            f"Frame {frame_idx}/{reader.frame_count}",
            f"Detections: {len(detections)}",
            f"Inference FPS: {fps_estimate:.1f}",
        ])

        writer.write(frame)

    writer.release()
    elapsed = time.time() - start_time
    avg_fps = frame_idx / elapsed if elapsed > 0 else 0.0

    print(f"Processed {frame_idx} frames in {elapsed:.1f}s ({avg_fps:.1f} avg fps)")
    print(f"Total detections across all frames: {total_detections}")
    print(f"Average detections/frame: {total_detections / frame_idx:.1f}")
    print(f"Annotated video saved to: {out_path}")


if __name__ == "__main__":
    main()
