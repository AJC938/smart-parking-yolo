"""Debug: verify Ultralytics built-in ByteTrack works with the OBB task."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO
from config import config

model = YOLO(config.YOLO_MODEL_PATH)

results = model.track(
    source=str(config.VIDEO_PATH),
    conf=config.CONFIDENCE_THRESHOLD,
    imgsz=config.IMAGE_SIZE,
    classes=list(config.VEHICLE_CLASS_IDS),
    tracker=config.TRACKER_CONFIG,
    persist=True,
    stream=True,
    verbose=False,
)

for i, r in enumerate(results):
    obb = r.obb
    if obb is None or obb.id is None:
        print(f"frame {i}: no tracked obb (obb is None: {obb is None})")
    else:
        ids = obb.id.tolist()
        print(f"frame {i}: {len(ids)} tracked -> ids={ids}")
    if i >= 15:
        break
