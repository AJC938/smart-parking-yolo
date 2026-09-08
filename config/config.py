"""Central configuration for the Smart Parking Intelligence System.

Keeping every tunable value here avoids magic numbers scattered
through the detection / tracking / parking / backend / GUI layers.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Video / input ---
VIDEO_PATH = PROJECT_ROOT / "data" / "input" / "parking_video.mp4"

# --- YOLO detection ---
# NOTE: This project's source video is a true top-down / nadir drone shot.
# Standard COCO-pretrained YOLO models (n/s/m, any image size) were tested
# and produce ZERO vehicle detections on this camera angle -- COCO's car
# images are all street-level/side views, which is out-of-distribution for
# a bird's-eye view (cars get misread as "cell phone", see docs/model_notes.md).
# Ultralytics' own DOTA-pretrained OBB model (aerial/satellite imagery,
# yolo11n-obb.pt) reliably localizes the vehicles instead, so it is used
# here in place of the standard detection model.
YOLO_MODEL_PATH = "yolo11n-obb.pt"  # Ultralytics OBB model, pretrained on DOTAv1 (aerial imagery)
CONFIDENCE_THRESHOLD = 0.2
IMAGE_SIZE = 640
# DOTA class ids that correspond to vehicles in this scene. "ship" (1) is
# included deliberately: at this drone altitude, cars are proportioned
# closer to DOTA's "ship" exemplars than its (much smaller/higher-altitude)
# "small vehicle"/"large vehicle" exemplars -- verified empirically, see
# docs/model_notes.md. All three are reported to the rest of the system
# under a single unified "vehicle" label.
VEHICLE_CLASS_IDS = {1, 9, 10}
VEHICLE_CLASS_NAMES = {1: "vehicle", 9: "vehicle", 10: "vehicle"}
# Sanity bounds (axis-aligned bbox area, in pixels) to reject detections
# that are clearly not a single parked vehicle at this frame resolution.
VEHICLE_MIN_AREA = 1500
VEHICLE_MAX_AREA = 12000

# --- Tracking ---
# Custom-tuned ByteTrack config (see the file for rationale); falls back to
# the string name "bytetrack.yaml" if the custom file is ever removed.
TRACKER_CONFIG = str(PROJECT_ROOT / "config" / "bytetrack_custom.yaml")

# --- Parking spaces ---
PARKING_SPACES_PATH = PROJECT_ROOT / "config" / "parking_spaces.json"
# Fraction of a vehicle's bounding-box area that must overlap a stall
# polygon for the stall to be considered occupied by that vehicle.
OCCUPANCY_OVERLAP_THRESHOLD = 0.3
# Number of consecutive frames a status must hold before it is reported,
# to suppress single-frame flicker.
OCCUPANCY_STABILITY_FRAMES = 5

# --- Output ---
OUTPUT_DIR = PROJECT_ROOT / "outputs"
ANNOTATED_VIDEO_PATH = OUTPUT_DIR / "annotated_video.mp4"
LOG_DIR = OUTPUT_DIR / "logs"

# --- Backend ---
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000

# --- GUI ---
GUI_WINDOW_TITLE = "Smart Parking Intelligence"
GUI_REFRESH_MS = 30  # ~33 FPS UI refresh
