"""Phase 8 milestone: background pipeline worker updates shared AppState.

Run directly: python tests/test_phase8_pipeline_worker.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.state import AppState
from src.backend.pipeline import PipelineWorker


def main():
    state = AppState()
    worker = PipelineWorker(state)
    worker.start()

    for i in range(6):
        time.sleep(1)
        snap = state.snapshot()
        print(
            f"t={i+1}s frame_idx={snap.frame_index} fps={snap.fps:.1f} "
            f"occupied={snap.occupied_spaces}/{snap.total_spaces} "
            f"system(video={snap.system.video_ok}, yolo={snap.system.yolo_ok}, "
            f"tracking={snap.system.tracking_ok}, backend={snap.system.backend_ok}, "
            f"err='{snap.system.error_message}')"
        )
        if snap.frame is not None:
            print(f"  frame shape: {snap.frame.shape}")

    worker.stop()
    print("Worker stopped cleanly")


if __name__ == "__main__":
    main()
