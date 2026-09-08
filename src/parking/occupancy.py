"""Parking occupancy engine: associates vehicle detections with parking
spaces (not just "how many cars exist"), and stabilizes the result over
time to avoid flicker.

Method: for each (space, vehicle) pair, compute what fraction of the
vehicle's bounding box overlaps the space's polygon (via Sutherland-Hodgman
clipping, so it generalizes to any convex polygon, not just rectangles). A
space is a raw-occupied candidate if any vehicle clears
OCCUPANCY_OVERLAP_THRESHOLD; the best-overlapping vehicle "wins" the space.
A per-space streak counter then requires OCCUPANCY_STABILITY_FRAMES
consecutive frames of a status before it is actually reported, so a single
missed/duplicate detection doesn't flip a space's displayed status.
"""
from dataclasses import dataclass

from config import config
from src.parking.space import ParkingSpace


def _clip_polygon_to_rect(polygon: list[tuple[float, float]], rect: tuple[float, float, float, float]):
    """Sutherland-Hodgman clip of `polygon` against axis-aligned `rect` (x1,y1,x2,y2)."""
    x1, y1, x2, y2 = rect

    def clip_edge(points, inside_fn, intersect_fn):
        if not points:
            return []
        output = []
        prev = points[-1]
        prev_inside = inside_fn(prev)
        for curr in points:
            curr_inside = inside_fn(curr)
            if curr_inside:
                if not prev_inside:
                    output.append(intersect_fn(prev, curr))
                output.append(curr)
            elif prev_inside:
                output.append(intersect_fn(prev, curr))
            prev, prev_inside = curr, curr_inside
        return output

    def lerp(p1, p2, t):
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))

    edges = [
        (lambda p: p[0] >= x1, lambda p1, p2: lerp(p1, p2, (x1 - p1[0]) / (p2[0] - p1[0]))),
        (lambda p: p[0] <= x2, lambda p1, p2: lerp(p1, p2, (x2 - p1[0]) / (p2[0] - p1[0]))),
        (lambda p: p[1] >= y1, lambda p1, p2: lerp(p1, p2, (y1 - p1[1]) / (p2[1] - p1[1]))),
        (lambda p: p[1] <= y2, lambda p1, p2: lerp(p1, p2, (y2 - p1[1]) / (p2[1] - p1[1]))),
    ]

    output = list(polygon)
    for inside_fn, intersect_fn in edges:
        output = clip_edge(output, inside_fn, intersect_fn)
        if not output:
            return []
    return output


def _polygon_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    area = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def overlap_fraction(vehicle_bbox: tuple[float, float, float, float], space_polygon: list[tuple[int, int]]) -> float:
    """Fraction of the vehicle's bbox area that lies inside the space polygon."""
    x1, y1, x2, y2 = vehicle_bbox
    vehicle_area = (x2 - x1) * (y2 - y1)
    if vehicle_area <= 0:
        return 0.0
    clipped = _clip_polygon_to_rect(space_polygon, vehicle_bbox)
    return _polygon_area(clipped) / vehicle_area


@dataclass
class ParkingStats:
    total_spaces: int
    occupied_spaces: int
    available_spaces: int
    occupancy_rate: float


class OccupancyEngine:
    def __init__(
        self,
        overlap_threshold: float = config.OCCUPANCY_OVERLAP_THRESHOLD,
        stability_frames: int = config.OCCUPANCY_STABILITY_FRAMES,
    ):
        self.overlap_threshold = overlap_threshold
        self.stability_frames = stability_frames

    def update(self, spaces: list[ParkingSpace], detections: list) -> ParkingStats:
        """Update each space's occupied/available status.

        Uses a bounded confidence counter with hysteresis rather than a
        strict "N consecutive frames" streak: the detector's recall is
        imperfect (see docs/model_notes.md), so a single missed detection
        on an otherwise-parked car must not wipe out prior evidence. The
        counter rises on a positive frame and falls on a negative one
        (capped at 0..stability_frames*2), and status flips only once it
        crosses the enter/exit thresholds -- this still filters out
        single-frame flicker while tolerating a detector with ~50-80%
        per-frame recall on a genuinely parked vehicle.
        """
        enter_threshold = self.stability_frames
        confidence_cap = self.stability_frames * 2

        for space in spaces:
            best_overlap = 0.0
            best_track_id = None
            for det in detections:
                frac = overlap_fraction((det.x1, det.y1, det.x2, det.y2), space.polygon)
                if frac > best_overlap:
                    best_overlap = frac
                    best_track_id = getattr(det, "track_id", None)

            raw_occupied = best_overlap >= self.overlap_threshold

            # `occupied_streak` doubles as a bounded confidence counter (not
            # a strict run-length): it rises on a hit and falls on a miss,
            # so isolated misses only nudge it down instead of zeroing it.
            if raw_occupied:
                space.occupied_streak = min(space.occupied_streak + 1, confidence_cap)
            else:
                space.occupied_streak = max(space.occupied_streak - 1, 0)

            if not space.occupied and space.occupied_streak >= enter_threshold:
                space.occupied = True
            elif space.occupied and space.occupied_streak <= 0:
                space.occupied = False
                space.vehicle_track_id = None

            if space.occupied and raw_occupied:
                space.vehicle_track_id = best_track_id

        occupied_count = sum(1 for s in spaces if s.occupied)
        total = len(spaces)
        return ParkingStats(
            total_spaces=total,
            occupied_spaces=occupied_count,
            available_spaces=total - occupied_count,
            occupancy_rate=(occupied_count / total * 100.0) if total else 0.0,
        )
