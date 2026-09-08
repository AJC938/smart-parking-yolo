# Input Video Analysis — `parking_video.mp4`

Source: `istockphoto-1370353417-640_adpp_is.mp4` (iStock/Getty stock footage, used locally for development only — contains a visible watermark).

## Technical properties
- Resolution: 768x432
- FPS: 24.0
- Frame count: 400
- Duration: ~16.7 seconds

## Scene characteristics
- **Camera angle:** Top-down / aerial (drone) view, near-orthographic — minimal perspective distortion on vehicles.
- **Camera stability:** Fully static lock-off shot. (An initial visual read suggested a slow horizontal drift, but direct measurement -- phase correlation and template matching between frame 0 and frame 399 on several static features, see `scripts/debug_*` history -- found ~0px shift. The parking-space polygons are anchored to fixed frame-0 pixel coordinates with no drift compensation needed.)
- **Layout:** Two rows of parking stalls facing each other across a central driving/walking aisle, oriented top row (cars pointing "down" toward aisle) and bottom row (cars pointing "up" toward aisle).
- **Visible spaces:** ~12 stalls per row (~24 total), several partially cut off at the left/right frame edges. Stall boundaries are painted white U-shaped lines, clearly visible from above.
- **Vehicle size:** Fairly uniform (~70-95px wide x ~130-155px tall) due to the overhead angle — little size variation across the frame, which simplifies detection.
- **Occlusion:** Minimal — the top-down angle avoids most car-to-car occlusion. Vehicles are cleanly separated by stall lines.
- **Lighting:** Consistent, bright daylight, consistent shadow direction throughout.
- **Moving objects:** One vehicle briefly drives through the central aisle (confirmed visually around frame ~51/400) — a useful real test of the tracker on a genuinely moving object. Pedestrians and a shopping-cart rack (stationary in one bottom-row stall) are also present and must NOT be misclassified as vehicles.
- **Important discovered characteristic — this is a stylized "lot emptying" edit, not a static plate:** individual parked vehicles visibly fade out (roof/body dissolve away while their ground shadow briefly remains, then that fades too) at *different points* in the clip rather than all at once — confirmed by direct frame inspection (`scripts/debug_*` scripts) around frames 220-360, where cars disappear one by one until only 1-2 remain tracked by the final frames. This is a deliberate editorial effect in the source stock footage (a "before/after" or time-lapse-style dissolve), not a bug, camera issue, or detector failure. It means occupancy genuinely and correctly decreases over the course of this specific clip — a fitting real-world-like scenario for demonstrating the system's live occupancy tracking, and the reason the annotated output video's occupied count trends down over its 16.7s runtime.
- **Known edge cases in this specific video:**
  - One bottom-row stall contains only a wheel-stop and no vehicle (clear AVAILABLE test case).
  - One bottom-row stall is occupied by a stacked shopping-cart rack, not a vehicle — the system will correctly report this as AVAILABLE since no *vehicle* is detected there (documented limitation: occupancy is vehicle-based, not general-object-based).
  - A semi-transparent "iStock by Getty Images" watermark sits in the middle of the frame (over the aisle, not over any vehicle), so it does not interfere with detections.

## Design implications
- A top-down view is ideal for a **bounding-box/polygon overlap-fraction** occupancy method (see `src/parking/occupancy.py`) — no need for complex perspective-aware IoU.
- Because individual vehicles fade in/out and one drives through the aisle, the tracker's ID stability plus the occupancy engine's hysteresis-based confidence counter (`docs/model_notes.md`) both matter here, not just for hypothetical future footage.
- Parking-space polygons were hand-defined against actual pixel coordinates from sampled frames (see `config/parking_spaces.json`), not guessed.
