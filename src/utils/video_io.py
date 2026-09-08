"""Video reading/writing helpers shared across the pipeline."""
from pathlib import Path

import cv2


class VideoReader:
    def __init__(self, path: Path):
        if not Path(path).exists():
            raise FileNotFoundError(f"Video file not found: {path}")

        self.cap = cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise IOError(f"Could not open video: {path}")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            raise StopIteration
        return frame

    def release(self):
        self.cap.release()


class VideoWriter:
    def __init__(self, path: Path, width: int, height: int, fps: float):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
        if not self.writer.isOpened():
            raise IOError(f"Could not open video writer for: {path}")

    def write(self, frame):
        self.writer.write(frame)

    def release(self):
        self.writer.release()
