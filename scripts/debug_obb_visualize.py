"""Debug: draw OBB detections on the frame regardless of class label, to
verify positional accuracy of the DOTA model on our vehicles."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np
from ultralytics import YOLO
from config import config

img = cv2.imread(str(config.OUTPUT_DIR / "screenshots" / "sample_frame_0_idx0.jpg"))
model = YOLO("yolo11n-obb.pt")
results = model.predict(img, conf=0.15, imgsz=640, verbose=False)
r = results[0]

out = img.copy()
if r.obb is not None:
    for i in range(len(r.obb)):
        pts = r.obb.xyxyxyxy[i].cpu().numpy().astype(np.int32)
        cid = int(r.obb.cls[i])
        conf = float(r.obb.conf[i])
        cv2.polylines(out, [pts], True, (0, 255, 0), 2)
        label = f"{model.names[cid]} {conf:.2f}"
        cv2.putText(out, label, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)

out_path = config.OUTPUT_DIR / "screenshots" / "obb_debug_overlay.jpg"
cv2.imwrite(str(out_path), out)
print(f"Saved {out_path}, detections={0 if r.obb is None else len(r.obb)}")
