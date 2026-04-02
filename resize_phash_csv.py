import cv2
import imagehash
import os
import csv
import time
from PIL import Image
import numpy as np

# Config
_MARGIN_SIZE_IN_PIXELS = 150
FRAME_INTERVAL = 1  # Number of frames to skip; 1 = every frame
CSV_PATH = "all_resize_hashes.csv"
TARGET_RESOLUTION = (800, 800)  # width x height

FOLDERS_TO_PROCESS = [
    "downloads",
    "processed/reels_processed",
    "processed/shorts_processed"
]

# Utilities
def process_frame_in_memory(frame):
    """Resize, crop margins, convert to PIL image, and compute pHash."""
    # Resize to 800x800
    resized = cv2.resize(frame, TARGET_RESOLUTION)

    # Remove margins
    h, w = resized.shape[:2]
    cropped = resized[_MARGIN_SIZE_IN_PIXELS:h-_MARGIN_SIZE_IN_PIXELS,
                      _MARGIN_SIZE_IN_PIXELS:w-_MARGIN_SIZE_IN_PIXELS]

    # Convert BGR → RGB for PIL
    rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    # Compute phash
    phash = imagehash.phash(pil_img)
    return phash

# Use for every frame
def compute_hashes_for_video(video_path, frame_interval=FRAME_INTERVAL):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    hashes = []
    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            phash = process_frame_in_memory(frame)
            hashes.append(phash)
            saved_frame_count += 1

        frame_count += 1

    cap.release()
    return hashes

# Use for fixed FPS (e.g., 1 frame per second)
def compute_hashes_for_fixed_fps_video(video_path, desired_fps=1):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fallback if FPS is 0
    frame_interval = max(int(fps / desired_fps), 1)

    hashes = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            phash = process_frame_in_memory(frame)
            hashes.append(phash)

        frame_count += 1

    cap.release()
    return hashes

def save_hashes_to_csv(video_path, hashes, processing_time, csv_path=CSV_PATH):
    video_name = os.path.basename(video_path)
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['video', 'frame', 'phash', 'processing_seconds'])

        for i, h in enumerate(hashes):
            writer.writerow([video_name, i, str(h), processing_time])

# Main
def main():
    for folder in FOLDERS_TO_PROCESS:
        folder_path = os.path.abspath(folder)
        if not os.path.exists(folder_path):
            print(f"Skipping missing folder: {folder_path}")
            continue

        for file_name in os.listdir(folder_path):
            if not file_name.lower().endswith((".mp4", ".mov", ".mkv")):
                continue

            video_path = os.path.join(folder_path, file_name)
            print(f"Processing: {video_path}")

            start_time = time.time()
            # hashes = compute_hashes_for_video(video_path) # Use every frame
            hashes_1fps = compute_hashes_for_fixed_fps_video(video_path, desired_fps=1) # Use fixed fps (~1 frame per second)
            end_time = time.time()

            processing_time = round(end_time - start_time, 3)
            save_hashes_to_csv(video_path, hashes_1fps, processing_time)
            print(f"Saved hashes for {file_name}, processed in {processing_time} seconds")

if __name__ == "__main__":
    main()