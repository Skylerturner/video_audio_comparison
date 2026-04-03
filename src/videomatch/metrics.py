import sys
import time
import csv
import numpy as np
from scipy.spatial.distance import cosine

SLIDING_WINDOW_SIZE = 5

# --- Shared ---

def compare_all(target_video_path, target_hashes, comparison_videos, metric_fn, close_threshold):
    results = []
    for video, hashes in comparison_videos.items():
        start_time = time.time()
        metrics = metric_fn(target_hashes, hashes, close_threshold)
        end_time = time.time()
        comparison_time = round(end_time - start_time, 6)

        if metrics:
            metrics["video"] = video
            metrics["target_video_path"] = target_video_path
            metrics["comparison_seconds"] = comparison_time
            results.append(metrics)
    return results

def save_metrics(results, output_csv):
    if not results:
        print("No results to save.")
        return
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

# --- Standard phash comparison ---

def compute_phash_metrics(target_hashes, other_hashes, close_threshold=8):
    diffs = []
    global_min_diff = sys.maxsize
    min_target_frame = None
    min_other_frame = None

    for i, h1 in enumerate(target_hashes):
        min_diff_for_frame = sys.maxsize
        for j, h2 in enumerate(other_hashes):
            diff = abs(h1 - h2)
            if diff < min_diff_for_frame:
                min_diff_for_frame = diff
            if diff < global_min_diff:
                global_min_diff = diff
                min_target_frame = i
                min_other_frame = j
        diffs.append(min_diff_for_frame)

    if not diffs:
        return None

    min_diff = min(diffs)
    max_diff = max(diffs)
    avg_diff = sum(diffs) / len(diffs)
    close_matches = sum(1 for d in diffs if d < close_threshold)

    return {
        "min_diff": min_diff,
        "min_target_frame": min_target_frame,
        "min_other_frame": min_other_frame,
        "max_diff": max_diff,
        "range": max_diff - min_diff,
        "avg_diff": avg_diff,
        "percent_close": close_matches / len(diffs)
    }

# --- Kernel phash comparison ---

def compute_phash_metrics_kernel(target_hashes, other_hashes, close_threshold=10):
    diffs = []
    global_min_diff = sys.maxsize
    min_target_frame = None
    min_other_frame = None

    N = len(target_hashes)
    M = len(other_hashes)
    window_size = max(1, N // M)

    for j, h2 in enumerate(other_hashes):
        start_idx = j * window_size
        end_idx = min((j + 1) * window_size, N)
        min_diff_for_frame = sys.maxsize

        for i in range(start_idx, end_idx):
            diff = abs(target_hashes[i] - h2)
            if diff < min_diff_for_frame:
                min_diff_for_frame = diff
            if diff < global_min_diff:
                global_min_diff = diff
                min_target_frame = i
                min_other_frame = j

        diffs.append(min_diff_for_frame)

    if not diffs:
        return None

    min_diff = min(diffs)
    max_diff = max(diffs)
    close_matches = sum(1 for d in diffs if d < close_threshold)

    return {
        "min_diff": min_diff,
        "min_target_frame": min_target_frame,
        "min_other_frame": min_other_frame,
        "max_diff": max_diff,
        "range": max_diff - min_diff,
        "avg_diff": sum(diffs) / len(diffs),
        "percent_close": close_matches / len(diffs)
    }

# --- Audio comparison ---

def compute_audio_metrics(target_hashes, other_hashes, close_threshold=0.15):
    len1 = len(target_hashes)
    len2 = len(other_hashes)

    if len1 == 0 or len2 == 0:
        return None

    window_size = min(SLIDING_WINDOW_SIZE, len1, len2)
    diffs = []
    min_diff = float("inf")
    min_target_frame = None
    min_other_frame = None

    for i in range(len1 - window_size + 1):
        window1 = np.mean(target_hashes[i:i+window_size], axis=0)
        for j in range(len2 - window_size + 1):
            window2 = np.mean(other_hashes[j:j+window_size], axis=0)
            diff = cosine(window1, window2)
            diffs.append(diff)
            if diff < min_diff:
                min_diff = diff
                min_target_frame = i
                min_other_frame = j

    if not diffs:
        return None

    max_diff = max(diffs)
    close_matches = sum(1 for d in diffs if d < close_threshold)

    return {
        "min_diff": round(min_diff, 10),
        "min_target_frame": min_target_frame,
        "min_other_frame": min_other_frame,
        "max_diff": round(max_diff, 10),
        "range": round(max_diff - min_diff, 10),
        "avg_diff": round(sum(diffs) / len(diffs), 10),
        "percent_close": round(close_matches / len(diffs), 10)
    }