from dataclasses import dataclass

import pytest

from src.parking.occupancy import OccupancyEngine, overlap_fraction
from src.parking.space import ParkingSpace


@dataclass
class FakeDetection:
    x1: float
    y1: float
    x2: float
    y2: float
    track_id: int = 1


def test_overlap_fraction_full_containment():
    space_polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    vehicle_bbox = (10, 10, 50, 50)  # fully inside
    assert overlap_fraction(vehicle_bbox, space_polygon) == pytest.approx(1.0)


def test_overlap_fraction_no_overlap():
    space_polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    vehicle_bbox = (200, 200, 250, 250)
    assert overlap_fraction(vehicle_bbox, space_polygon) == pytest.approx(0.0)


def test_overlap_fraction_partial_overlap():
    space_polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
    vehicle_bbox = (50, 50, 150, 150)  # half in, half out
    # intersection is the 50x50 square [50,50]-[100,100]; vehicle area is 100x100
    assert overlap_fraction(vehicle_bbox, space_polygon) == pytest.approx(0.25)


def test_engine_requires_several_frames_before_reporting_occupied():
    engine = OccupancyEngine(overlap_threshold=0.3, stability_frames=5)
    space = ParkingSpace(id="P01", polygon=[(0, 0), (100, 0), (100, 100), (0, 100)])
    vehicle = [FakeDetection(10, 10, 50, 50)]

    for _ in range(4):
        stats = engine.update([space], vehicle)
        assert space.occupied is False

    stats = engine.update([space], vehicle)
    assert space.occupied is True
    assert stats.occupied_spaces == 1


def test_engine_tolerates_a_single_missed_frame():
    """A car doesn't vanish because the detector missed it for one frame."""
    engine = OccupancyEngine(overlap_threshold=0.3, stability_frames=5)
    space = ParkingSpace(id="P01", polygon=[(0, 0), (100, 0), (100, 100), (0, 100)])
    vehicle = [FakeDetection(10, 10, 50, 50)]

    for _ in range(6):
        engine.update([space], vehicle)
    assert space.occupied is True

    engine.update([space], [])  # one missed frame
    assert space.occupied is True  # must not flip immediately

    engine.update([space], vehicle)
    assert space.occupied is True


def test_engine_reports_available_when_vehicle_leaves():
    engine = OccupancyEngine(overlap_threshold=0.3, stability_frames=3)
    space = ParkingSpace(id="P01", polygon=[(0, 0), (100, 0), (100, 100), (0, 100)])
    vehicle = [FakeDetection(10, 10, 50, 50)]

    for _ in range(5):
        engine.update([space], vehicle)
    assert space.occupied is True

    for _ in range(10):
        engine.update([space], [])
    assert space.occupied is False
    assert space.vehicle_track_id is None


def test_empty_space_never_flagged_occupied_by_unrelated_object():
    engine = OccupancyEngine()
    space = ParkingSpace(id="P12", polygon=[(0, 0), (100, 0), (100, 100), (0, 100)])
    unrelated = [FakeDetection(500, 500, 550, 550)]

    for _ in range(20):
        engine.update([space], unrelated)
    assert space.occupied is False
