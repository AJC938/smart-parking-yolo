"""Debug: test the DOTA-pretrained OBB YOLO model (designed for aerial
imagery) against the standard COCO model on our overhead parking frame."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO
from config import config

img = cv2.imread(str(config.OUTPUT_DIR / "screenshots" / "sample_frame_0_idx0.jpg"))

model = YOLO("yolo11n-obb.pt")
print("OBB model class names:", model.names)

for conf in [0.35, 0.2, 0.1]:
    results = model.predict(img, conf=conf, imgsz=640, verbose=False)
    r = results[0]
    n = len(r.obb) if r.obb is not None else 0
    print(f"--- conf={conf}: {n} detections ---")
    if r.obb is not None:
        for i in range(min(n, 40)):
            cid = int(r.obb.cls[i])
            print(f"    {model.names[cid]} conf={float(r.obb.conf[i]):.2f}")
