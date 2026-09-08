import pytest

from config import config
from src.detection.detector import Detection, VehicleDetector
from src.utils.video_io import VideoReader


@pytest.fixture(scope="module")
def detector():
    return VehicleDetector()


@pytest.fixture(scope="module")
def first_frame():
    reader = VideoReader(config.VIDEO_PATH)
    frame = next(reader)
    reader.release()
    return frame


def test_detector_finds_vehicles_on_first_frame(detector, first_frame):
    detections = detector.detect(first_frame)
    assert len(detections) > 5  # should find most of the ~14 visible vehicles
    assert all(isinstance(d, Detection) for d in detections)


def test_detections_are_within_frame_bounds(detector, first_frame):
    h, w = first_frame.shape[:2]
    detections = detector.detect(first_frame)
    for d in detections:
        assert 0 <= d.x1 < d.x2 <= w
        assert 0 <= d.y1 < d.y2 <= h


def test_detections_pass_area_sanity_filter(detector, first_frame):
    detections = detector.detect(first_frame)
    for d in detections:
        area = (d.x2 - d.x1) * (d.y2 - d.y1)
        assert config.VEHICLE_MIN_AREA <= area <= config.VEHICLE_MAX_AREA


def test_invalid_model_path_raises():
    with pytest.raises(RuntimeError):
        VehicleDetector(model_path="not_a_real_model_file.pt")
