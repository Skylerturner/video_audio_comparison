import cv2
import imagehash
import os
import shutil
import sys
import uuid
from PIL import Image

_RECORDING_FILE_NOT_FOUND_ERROR = 1
_AD_FILE_NOT_FOUND_ERROR = 2
_NO_HASH_DIFF_ERROR = 3
_MARGIN_SIZE_IN_PIXELS = 30

def clean_dir(dir_path):
    if not os.path.exists(dir_path):
        return
    
    shutil.rmtree(dir_path)

def extract_frames(video_path, output_dir, frame_interval=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()

        # If no more frames, break the loop
        if not ret:
            break

        # Crop around the frame
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
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            file_hash = get_image_hash(file_path)
            directory_hashes.append(file_hash)
    
    return directory_hashes

def get_match_diffs(recording_hashes, ad_hashes):
    matches = []
    for hash1 in recording_hashes:
        min_hash_diff = sys.maxsize
        for hash2 in ad_hashes:
            hash_diff = abs(hash1 - hash2)
            if hash_diff < min_hash_diff:
                min_hash_diff = hash_diff
        matches.append(min_hash_diff)
    return matches

def main():
    args = sys.argv[1:]

    recording_local_path = args[0]
    if not os.path.exists(recording_local_path):
        sys.exit(_RECORDING_FILE_NOT_FOUND_ERROR)
    
    ad_local_path = args[1]
    if not os.path.exists(ad_local_path):
        sys.exit(_AD_FILE_NOT_FOUND_ERROR)

    unique_id = str(uuid.uuid4())
    extracted_recording_frames_dir_path = f"./extracted_frames/recording_frames_{unique_id}"
    extracted_ad_frames_dir_path = f"./extracted_frames/ad_frames_{unique_id}"

    extract_frames(recording_local_path, extracted_recording_frames_dir_path)
    extract_frames(ad_local_path, extracted_ad_frames_dir_path)

    recording_hashes = get_directory_hashes(extracted_recording_frames_dir_path)
    ad_hashes = get_directory_hashes(extracted_ad_frames_dir_path)

    match_diffs = get_match_diffs(recording_hashes, ad_hashes)
    min_diff = min(match_diffs)
    if min_diff == sys.maxsize:
        exit(_NO_HASH_DIFF_ERROR)
    print(min_diff)

    clean_dir(extracted_recording_frames_dir_path)
    clean_dir(extracted_ad_frames_dir_path)

if (__name__ == '__main__'):
    main()