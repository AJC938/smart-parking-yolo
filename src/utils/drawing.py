"""Shared OpenCV drawing helpers for annotating frames."""
import cv2

COLOR_DETECTION = (0, 200, 255)
COLOR_TEXT_BG = (0, 0, 0)


def draw_detection_box(frame, x1, y1, x2, y2, label: str, color=COLOR_DETECTION):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)


def draw_hud(frame, lines: list[str], origin=(10, 20), line_height=20):
    x, y = origin
    for i, line in enumerate(lines):
        y_pos = y + i * line_height
        (tw, th), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x - 4, y_pos - th - 4), (x + tw + 4, y_pos + 4), COLOR_TEXT_BG, -1)
        cv2.putText(frame, line, (x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
