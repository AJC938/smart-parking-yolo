from config import config
from src.tracking.tracker import TrackedDetection, VehicleTracker
from src.utils.video_io import VideoReader


def test_tracker_assigns_persistent_ids_across_frames():
    reader = VideoReader(config.VIDEO_PATH)
    tracker = VehicleTracker()

    frame1 = next(reader)
    frame2 = next(reader)

    tracks1 = tracker.update(frame1)
    tracks2 = tracker.update(frame2)
    reader.release()

    assert len(tracks1) > 0
    assert all(isinstance(t, TrackedDetection) for t in tracks1)

    ids1 = {t.track_id for t in tracks1}
    ids2 = {t.track_id for t in tracks2}
    # consecutive frames of a mostly-static scene should share most IDs
    assert len(ids1 & ids2) >= len(ids1) - 2


def test_tracker_ids_are_non_negative():
    reader = VideoReader(config.VIDEO_PATH)
    tracker = VehicleTracker()
    tracks = tracker.update(next(reader))
    reader.release()
    assert all(t.track_id >= 0 for t in tracks)
