"""Debug: run raw YOLO (all classes, very low conf) on one sample frame."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO
from config import config

img = cv2.imread(str(config.OUTPUT_DIR / "screenshots" / "sample_frame_0_idx0.jpg"))
model = YOLO("yolo11n.pt")

for conf in [0.35, 0.15, 0.05]:
    results = model.predict(img, conf=conf, imgsz=640, verbose=False)
    print(f"--- conf={conf} ---")
    for result in results:
        for box in result.boxes:
            cid = int(box.cls[0])
            name = model.names[cid]
            print(f"  class={name} conf={float(box.conf[0]):.3f} box={box.xyxy[0].tolist()}")
    if len(results[0].boxes) == 0:
        print("  (no detections)")
