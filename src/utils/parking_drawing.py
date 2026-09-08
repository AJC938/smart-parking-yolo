"""Drawing helpers for parking-space visualization."""
import cv2

COLOR_OCCUPIED = (0, 0, 220)
COLOR_AVAILABLE = (0, 200, 0)


def draw_parking_space(frame, space):
    color = COLOR_OCCUPIED if space.occupied else COLOR_AVAILABLE
    pts = space.polygon
    for i in range(len(pts)):
        cv2.line(frame, pts[i], pts[(i + 1) % len(pts)], color, 2)

    x1, y1, _, _ = space.bbox
    status = "OCCUPIED" if space.occupied else "AVAILABLE"
    label = f"{space.id}"
    cv2.putText(frame, label, (x1 + 4, y1 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    cv2.putText(frame, status, (x1 + 4, y1 + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
