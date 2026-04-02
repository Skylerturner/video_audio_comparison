import cv2
import imagehash
import os
import shutil
import uuid
import csv
import time
from PIL import Image

# Config
_MARGIN_SIZE_IN_PIXELS = 30
FRAME_INTERVAL = 1  # Number of frames to skip; 1 ~ 1 frame per second, 60 ~ 1 frame per minute
CSV_PATH = "all_hashes.csv"

FOLDERS_TO_PROCESS = [
    "downloads",
    "processed/reels_processed",
    "processed/shorts_processed"
]

# Utilities
def clean_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def extract_frames(video_path, output_dir, frame_interval=FRAME_INTERVAL):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width = frame.shape[:2]
        y_start = _MARGIN_SIZE_IN_PIXELS
        y_end = height - _MARGIN_SIZE_IN_PIXELS
        x_start = _MARGIN_SIZE_IN_PIXELS
        x_end = width - _MARGIN_SIZE_IN_PIXELS
        cropped_frame = frame[y_start:y_end, x_start:x_end]

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_dir, f"frame_{saved_frame_count:07d}.jpg")
            cv2.imwrite(frame_filename, cropped_frame)
            saved_frame_count += 1

        frame_count += 1

    cap.release()

def get_image_hash(file_path):
    with Image.open(file_path) as img:
        return imagehash.phash(img)

def get_directory_hashes(dir_path):
    directory_hashes = []
    for file_name in sorted(os.listdir(dir_path)):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            directory_hashes.append(get_image_hash(file_path))
    return directory_hashes

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

            unique_id = str(uuid.uuid4())
            temp_frame_dir = f"./temp_frames_{unique_id}"

            start_time = time.time()

            extract_frames(video_path, temp_frame_dir)
            hashes = get_directory_hashes(temp_frame_dir)

            end_time = time.time()
            processing_time = round(end_time - start_time, 3)
            save_hashes_to_csv(video_path, hashes, processing_time)

            clean_dir(temp_frame_dir)
            print(f"Saved hashes for {file_name}, processed in {processing_time} seconds")

if __name__ == "__main__":
    main()