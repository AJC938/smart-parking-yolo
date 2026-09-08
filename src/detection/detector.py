"""YOLO-based vehicle detection layer.

Wraps an Ultralytics YOLO model and exposes a simple `detect()` method
that returns only the vehicle classes the parking system cares about.
"""
from dataclasses import dataclass

from ultralytics import YOLO

from config import config


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str

    @property
    def center(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2


class VehicleDetector:
    def __init__(
        self,
        model_path: str = config.YOLO_MODEL_PATH,
        confidence_threshold: float = config.CONFIDENCE_THRESHOLD,
        image_size: int = config.IMAGE_SIZE,
    ):
        try:
            self.model = YOLO(model_path)
        except Exception as exc:
            raise RuntimeError(f"Failed to load YOLO model '{model_path}': {exc}") from exc

        self.confidence_threshold = confidence_threshold
        self.image_size = image_size

    def detect(self, frame) -> list[Detection]:
        """Run OBB inference and return axis-aligned vehicle detections.

        The model outputs oriented boxes (4 corner points); since the source
        video is near-nadir, converting to an axis-aligned bbox is accurate
        enough and keeps downstream parking-overlap logic simple.
        """
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            imgsz=self.image_size,
            classes=list(config.VEHICLE_CLASS_IDS),
            verbose=False,
        )

        detections: list[Detection] = []
        for result in results:
            obb = result.obb
            if obb is None:
                continue
            for i in range(len(obb)):
                class_id = int(obb.cls[i])
                points = obb.xyxyxyxy[i].cpu().numpy()
                x1, y1 = float(points[:, 0].min()), float(points[:, 1].min())
                x2, y2 = float(points[:, 0].max()), float(points[:, 1].max())

                area = (x2 - x1) * (y2 - y1)
                if not (config.VEHICLE_MIN_AREA <= area <= config.VEHICLE_MAX_AREA):
                    continue

                detections.append(
                    Detection(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=float(obb.conf[i]),
                        class_id=class_id,
                        class_name=config.VEHICLE_CLASS_NAMES.get(class_id, "vehicle"),
                    )
                )
        return detections
