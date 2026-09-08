import json

import pytest

from config import config
from src.parking.space import load_parking_spaces


def test_loads_configured_spaces():
    spaces = load_parking_spaces(config.PARKING_SPACES_PATH)
    assert len(spaces) == 18
    ids = [s.id for s in spaces]
    assert ids[0] == "P01"
    assert len(set(ids)) == len(ids)  # all unique


def test_space_bbox_matches_polygon_extent():
    spaces = load_parking_spaces(config.PARKING_SPACES_PATH)
    p01 = next(s for s in spaces if s.id == "P01")
    assert p01.bbox == (45, 0, 128, 195)


def test_missing_config_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_parking_spaces(tmp_path / "nope.json")


def test_malformed_json_raises(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_parking_spaces(bad_file)


def test_missing_polygon_field_raises(tmp_path):
    bad_file = tmp_path / "bad_spaces.json"
    bad_file.write_text(json.dumps({"spaces": [{"id": "P01"}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_parking_spaces(bad_file)


def test_empty_spaces_list_raises(tmp_path):
    bad_file = tmp_path / "empty.json"
    bad_file.write_text(json.dumps({"spaces": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_parking_spaces(bad_file)
