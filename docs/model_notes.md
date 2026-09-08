# YOLO Model Selection Notes

## Problem
The source video (`docs/video_analysis.md`) is a true top-down/nadir drone
shot. Standard Ultralytics YOLO models are pretrained on COCO, whose "car"
images are essentially all street-level or oblique views.

**Empirical test** (`scripts/debug_raw_detect.py`, `scripts/debug_model_compare.py`):
tried `yolo11n.pt`, `yolo11s.pt`, `yolo11m.pt` at `imgsz` 640 and 1280,
confidence down to 0.05, on a sample frame with ~24 clearly visible cars.

**Result: 0 vehicle-class detections in every combination.** The nano model
even misclassified several cars as "cell phone" — a top-down car's compact,
reflective rectangular silhouette is closer to COCO's phone exemplars than
its side-view car exemplars.

## Fix
Ultralytics also distributes an official OBB (oriented bounding box) model
pretrained on **DOTA v1**, an aerial/satellite imagery dataset that includes
vehicle classes. This is a strong, justified fit for our exact camera
geometry — still an Ultralytics YOLO implementation, just the variant built
for aerial views instead of street-level COCO.

**Test** (`scripts/debug_obb_detect.py`, `scripts/debug_obb_visualize.py`) with
`yolo11n-obb.pt`: correctly localizes 13-19 of the ~24 visible vehicles per
frame with tight, well-aligned boxes.

One quirk: DOTA's "ship" class (id 1), not "small vehicle"/"large vehicle"
(ids 9/10), fires most consistently on our cars. This is a scale-domain
effect — DOTA's vehicle exemplars come from much higher satellite altitude
and are proportionally tiny, while our drone altitude renders cars at a size
closer to DOTA's ship exemplars. Verified by dumping raw box geometry: real
car hits cluster tightly at 33-50px x 80-111px (~2,700-5,400px² area)
regardless of whether the model calls them "ship" or "vehicle", while the one
spurious non-vehicle hit ("harbor") was 599x150px (~89,800px²) — an order of
magnitude larger.

## Final configuration (`config/config.py`)
- Model: `yolo11n-obb.pt`
- Vehicle class ids: `{1, 9, 10}` (ship, large vehicle, small vehicle),
  all reported to the rest of the system under one unified `"vehicle"` label
  — the DOTA label name is an implementation detail, not meaningful to the
  parking application.
- Confidence threshold: `0.2`
- Area sanity filter: `1500-12000 px²` axis-aligned bbox area, to reject
  outlier boxes like the "harbor" false hit without needing a second class
  to explicitly exclude.

## Limitations
- Recall is not perfect (~55-80% of visible vehicles per frame at these
  settings) since the model is still not fine-tuned for this exact scene.
  Tracking (Phase 5) and occupancy stability smoothing (Phase 9) absorb most
  of the resulting frame-to-frame flicker.
- A custom-trained model (e.g. fine-tuned on PKLot/CNRPark-style top-down
  parking data) would likely improve recall further, but is out of scope per
  the project's "do not over-engineer" guidance — this is a portfolio system
  built around one specific video, not a production detector.
