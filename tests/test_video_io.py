import pytest

from config import config
from src.utils.video_io import VideoReader


def test_video_loads_with_expected_properties():
    reader = VideoReader(config.VIDEO_PATH)
    assert reader.width == 768
    assert reader.height == 432
    assert reader.frame_count == 400
    assert reader.fps == pytest.approx(24.0, abs=0.1)
    reader.release()


def test_video_iterates_expected_frame_count():
    reader = VideoReader(config.VIDEO_PATH)
    count = sum(1 for _ in reader)
    assert count == 400


def test_missing_video_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        VideoReader(config.PROJECT_ROOT / "data" / "input" / "does_not_exist.mp4")
