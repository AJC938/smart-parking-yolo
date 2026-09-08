"""Unicode-safe image read/write helpers.

OpenCV's cv2.imread/cv2.imwrite use ANSI fopen() internally on Windows and
silently fail on non-ASCII paths (this project's folder path contains
Arabic characters). np.fromfile/tofile + cv2.imdecode/imencode route
through Python's own (Unicode-safe) file I/O instead, sidestepping the
limitation. Prefer these over cv2.imread/imwrite anywhere a path might
contain non-ASCII characters, e.g. saved screenshots.
"""
from pathlib import Path

import cv2
import numpy as np


def imread_unicode(path) -> np.ndarray | None:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except (FileNotFoundError, ValueError):
        return None


def imwrite_unicode(path, image: np.ndarray, ext: str = ".jpg") -> bool:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(ext, image)
    if not ok:
        return False
    encoded.tofile(str(path))
    return True
