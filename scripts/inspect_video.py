import cv2
import sys

path = "data/input/parking_video.mp4"
cap = cv2.VideoCapture(path)

if not cap.isOpened():
    print("ERROR: could not open video")
    sys.exit(1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps if fps else 0

print(f"Resolution: {width}x{height}")
print(f"FPS: {fps}")
print(f"Frame count: {frame_count}")
print(f"Duration: {duration:.2f} sec")

# Save a few sample frames for visual inspection
sample_indices = [0, frame_count // 4, frame_count // 2, (3 * frame_count) // 4, max(frame_count - 1, 0)]
for i, idx in enumerate(sample_indices):
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    if ret:
        out_path = f"outputs/screenshots/sample_frame_{i}_idx{idx}.jpg"
        cv2.imwrite(out_path, frame)
        print(f"Saved {out_path}")

cap.release()
