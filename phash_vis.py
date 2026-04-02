import cv2
import numpy as np
from PIL import Image
import imagehash
import os
import matplotlib.pyplot as plt

MARGIN = 30
HASH_SIZE = 8  # default for phash
TARGET_RESOLUTION = (800, 800)  # width x height

def get_nth_frame(video_path, frame_index=50):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video {video_path}")

    # Jump to the desired frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise Exception(f"Could not read frame {frame_index} from {video_path}")

    return frame

# def process_frame(frame):
#     steps = {}

#     # Step 0: Resize frame to TARGET_RESOLUTION (width x height)
#     frame_resized = cv2.resize(frame, TARGET_RESOLUTION)
#     frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
#     steps["original"] = frame_rgb

#     h, w = frame_resized.shape[:2]

#     # Crop margins
#     cropped = frame_resized[MARGIN:h-MARGIN, MARGIN:w-MARGIN]
#     cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
#     steps["cropped"] = cropped_rgb

#     # Convert to grayscale
#     gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
#     steps["grayscale"] = gray

#     # Resize for DCT
#     resized_for_dct = cv2.resize(gray, (HASH_SIZE * 4, HASH_SIZE * 4))
#     steps["resized_for_dct"] = resized_for_dct

#     # DCT spectrum
#     dct = cv2.dct(np.float32(resized_for_dct))
#     steps["dct"] = np.log(np.abs(dct) + 1)

#     # PIL image for phash
#     pil_img = Image.fromarray(gray)
#     phash = imagehash.phash(pil_img)

#     return steps, phash

def process_frame(frame):
    steps = {}

    # Original frame (no resize)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    steps["original"] = frame_rgb

    h, w = frame.shape[:2]

    # Crop margins from original frame
    cropped = frame[MARGIN:h-MARGIN, MARGIN:w-MARGIN]
    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    steps["cropped"] = cropped_rgb

    # Convert to grayscale
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    steps["grayscale"] = gray

    # Resize for DCT
    resized_for_dct = cv2.resize(gray, (HASH_SIZE * 4, HASH_SIZE * 4))
    steps["resized_for_dct"] = resized_for_dct

    # DCT spectrum
    dct = cv2.dct(np.float32(resized_for_dct))
    steps["dct"] = np.log(np.abs(dct) + 1)

    # PIL image for phash
    pil_img = Image.fromarray(gray)
    phash = imagehash.phash(pil_img)

    return steps, phash

def visualize(video_paths):
    num_videos = len(video_paths)
    num_steps = 6  # original, cropped, grayscale, resized, DCT, hash grid
    total_cols = num_steps + 1  # extra column for video filenames

    # Create a single figure with a grid: rows = videos, cols = steps + filename
    fig, axes = plt.subplots(num_videos, total_cols, figsize=(3*total_cols, 4*num_videos))

    # Ensure axes is 2D even if num_videos=1
    if num_videos == 1:
        axes = np.expand_dims(axes, axis=0)

    for row_idx, video in enumerate(video_paths):
        frame = get_nth_frame(video, frame_index=50)
        steps, phash = process_frame(frame)

        print(f"Video {row_idx+1}: {video} → pHash: {phash}")

        # First column: video filename as text
        ax = axes[row_idx, 0]
        ax.axis("off")

        # Get only the filename from the path
        filename = os.path.basename(video)

        ax.text(0.5, 0.5, filename, ha='center', va='center', fontsize=10)

        # Prepare images for the remaining columns
        images = [
            steps["original"],
            steps["cropped"],
            steps["grayscale"],
            steps["resized_for_dct"],
            steps["dct"],
            np.array(phash.hash, dtype=int)
        ]
        titles = [
            "Original Frame",
            f"After {MARGIN}px Crop",
            "Grayscale",
            "Resized (DCT Input)",
            "DCT Spectrum",
            "pHash 8x8 Grid"
        ]
        cmaps = [
            None, None, "gray", "gray", "inferno", "gray"
        ]

        for col_idx, (img, title, cmap) in enumerate(zip(images, titles, cmaps), start=1):
            ax = axes[row_idx, col_idx]
            ax.imshow(img, cmap=cmap, interpolation="nearest")
            ax.set_title(title, fontsize=9)
            ax.axis("off")

    plt.tight_layout()
    plt.suptitle("Video Processing Steps Comparison", fontsize=16, y=1.02)
    plt.show()

if __name__ == "__main__":
    video_files = [
        "downloads/scottkress_halloween_dl.mp4",
        "processed/reels_processed/scottkress_halloween_ig.mp4",
        "processed/shorts_processed/scottkress_halloween_yt.mp4"
    ]
    visualize(video_files)