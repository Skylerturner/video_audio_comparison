import cv2
import os
import shutil
import uuid
from PIL import Image
import imagehash

# --- Frame processing helpers ---

def crop_frame(frame, margin):
    h, w = frame.shape[:2]
    return frame[margin:h-margin, margin:w-margin]

def resize_frame(frame, target_resolution):
    return cv2.resize(frame, target_resolution)

def frame_to_phash(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return imagehash.phash(pil_img)

# --- Disk-based extraction (original method) ---

def extract_frames_to_disk(video_path, output_dir, frame_interval=1, margin=30):
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

        if frame_count % frame_interval == 0:
            cropped = crop_frame(frame, margin)
            frame_filename = os.path.join(output_dir, f"frame_{saved_frame_count:07d}.jpg")
            cv2.imwrite(frame_filename, cropped)
            saved_frame_count += 1

        frame_count += 1

    cap.release()

def hashes_from_disk(frame_dir):
    hashes = []
    for file_name in sorted(os.listdir(frame_dir)):
        file_path = os.path.join(frame_dir, file_name)
        if os.path.isfile(file_path):
            with Image.open(file_path) as img:
                hashes.append(imagehash.phash(img))
    return hashes

def extract_hashes_disk(video_path, frame_interval=1, margin=30):
    unique_id = str(uuid.uuid4())
    temp_dir = f"./temp_frames_{unique_id}"

    extract_frames_to_disk(video_path, temp_dir, frame_interval, margin)
    hashes = hashes_from_disk(temp_dir)

    shutil.rmtree(temp_dir)
    return hashes

# --- In-memory extraction (improved method) ---

def extract_hashes_in_memory(video_path, frame_interval=1, margin=150, target_resolution=(800, 800)):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    hashes = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            resized = resize_frame(frame, target_resolution)
            cropped = crop_frame(resized, margin)
            hashes.append(frame_to_phash(cropped))

        frame_count += 1

    cap.release()
    return hashes

def extract_hashes_fixed_fps(video_path, desired_fps=1, margin=150, target_resolution=(800, 800)):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = max(int(fps / desired_fps), 1)

    hashes = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            resized = resize_frame(frame, target_resolution)
            cropped = crop_frame(resized, margin)
            hashes.append(frame_to_phash(cropped))

        frame_count += 1

    cap.release()
    return hashes