"""Debug: draw candidate parking-space polygons over the source frame so
they can be visually checked against real stall lines and iterated on."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import cv2
from config import config
from src.utils.image_io import imread_unicode, imwrite_unicode

img = imread_unicode(config.OUTPUT_DIR / "screenshots" / "sample_frame_0_idx0.jpg")
out = img.copy()

with open(config.PARKING_SPACES_PATH) as f:
    spaces = json.load(f)["spaces"]

for space in spaces:
    pts = space["polygon"]
    for i in range(len(pts)):
        p1 = tuple(pts[i])
        p2 = tuple(pts[(i + 1) % len(pts)])
        cv2.line(out, p1, p2, (0, 0, 255), 2)
    cx = sum(p[0] for p in pts) // len(pts)
    cy = sum(p[1] for p in pts) // len(pts)
    cv2.putText(out, space["id"], (cx - 12, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

out = cv2.resize(out, (out.shape[1] * 2, out.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
out_path = config.OUTPUT_DIR / "screenshots" / "stall_overlay_check.jpg"
imwrite_unicode(out_path, out)
print(f"Saved {out_path}, {len(spaces)} spaces drawn")
