"""Parking-space data model and loader."""
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParkingSpace:
    id: str
    polygon: list[tuple[int, int]]
    row: str = ""
    occupied: bool = False
    occupied_streak: int = 0  # bounded hysteresis confidence counter, see OccupancyEngine
    vehicle_track_id: int | None = None

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        xs = [p[0] for p in self.polygon]
        ys = [p[1] for p in self.polygon]
        return min(xs), min(ys), max(xs), max(ys)


def load_parking_spaces(path: Path) -> list[ParkingSpace]:
    if not Path(path).exists():
        raise FileNotFoundError(f"Parking-space config not found: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed parking-space config '{path}': {exc}") from exc

    spaces = []
    for entry in data.get("spaces", []):
        if "id" not in entry or "polygon" not in entry:
            raise ValueError(f"Parking-space entry missing 'id' or 'polygon': {entry}")
        polygon = [tuple(p) for p in entry["polygon"]]
        if len(polygon) < 3:
            raise ValueError(f"Parking-space '{entry['id']}' polygon needs >= 3 points")
        spaces.append(ParkingSpace(id=entry["id"], polygon=polygon, row=entry.get("row", "")))

    if not spaces:
        raise ValueError(f"No parking spaces defined in '{path}'")

    return spaces
