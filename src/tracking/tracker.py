"""Vehicle tracking layer.

Consumes the same YOLO model as the detection layer but calls Ultralytics'
built-in `.track()` (ByteTrack by default) instead of `.predict()`, so
detections gain a persistent track ID across frames. This stabilizes the
parking-occupancy analysis and reduces frame-to-frame flicker; it is not a
separate AI model, just the tracking layer consuming YOLO's own detections.
"""
from dataclasses import dataclass

from ultralytics import YOLO

from config import config
from src.detection.detector import Detection


@dataclass
class TrackedDetection(Detection):
    track_id: int = -1


class VehicleTracker:
    def __init__(
        self,
        model_path: str = config.YOLO_MODEL_PATH,
        confidence_threshold: float = config.CONFIDENCE_THRESHOLD,
        image_size: int = config.IMAGE_SIZE,
        tracker_config: str = config.TRACKER_CONFIG,
    ):
        try:
            self.model = YOLO(model_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to load YOLO model '{model_path}': {exc}") from exc

        self.confidence_threshold = confidence_threshold
        self.image_size = image_size
        self.tracker_config = tracker_config

    def update(self, frame) -> list[TrackedDetection]:
        results = self.model.track(
            frame,
            conf=self.confidence_threshold,
            imgsz=self.image_size,
            classes=list(config.VEHICLE_CLASS_IDS),
            tracker=self.tracker_config,
            persist=True,
            verbose=False,
        )

        tracked: list[TrackedDetection] = []
        for result in results:
            obb = result.obb
            if obb is None or obb.id is None:
                continue
            for i in range(len(obb)):
                class_id = int(obb.cls[i])
                points = obb.xyxyxyxy[i].cpu().numpy()
                x1, y1 = float(points[:, 0].min()), float(points[:, 1].min())
                x2, y2 = float(points[:, 0].max()), float(points[:, 1].max())

                area = (x2 - x1) * (y2 - y1)
                if not (config.VEHICLE_MIN_AREA <= area <= config.VEHICLE_MAX_AREA):
                    continue

                tracked.append(
                    TrackedDetection(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=float(obb.conf[i]),
                        class_id=class_id,
                        class_name=config.VEHICLE_CLASS_NAMES.get(class_id, "vehicle"),
                        track_id=int(obb.id[i]),
                    )
                )
        return tracked
