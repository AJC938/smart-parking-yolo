"""Debug: compare YOLO model sizes / image sizes on a sample frame for the
overhead parking-lot scene, to pick settings that actually detect vehicles."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
from ultralytics import YOLO
from config import config

img = cv2.imread(str(config.OUTPUT_DIR / "screenshots" / "sample_frame_0_idx0.jpg"))
VEHICLE_IDS = {2, 3, 5, 7}

for model_name in ["yolo11n.pt", "yolo11s.pt", "yolo11m.pt"]:
    model = YOLO(model_name)
    for imgsz in [640, 1280]:
        results = model.predict(img, conf=0.1, imgsz=imgsz, verbose=False)
        boxes = results[0].boxes
        vehicle_hits = [b for b in boxes if int(b.cls[0]) in VEHICLE_IDS]
        print(f"{model_name} imgsz={imgsz}: total_boxes={len(boxes)} vehicle_boxes={len(vehicle_hits)}")
        for b in vehicle_hits[:5]:
            print(f"    {model.names[int(b.cls[0])]} conf={float(b.conf[0]):.2f}")
