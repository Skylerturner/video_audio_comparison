import csv
import sys
import time
import numpy as np
from scipy.spatial.distance import cosine

TARGET_CSV = "all_audio_hashes.csv"
COMPARISON_CSV = "all_audio_hashes.csv"
OUTPUT_CSV = "comparison_audio_metrics.csv"
close_threshold = 0.15  # Cosine distance threshold for "close" match
SLIDING_WINDOW_SIZE = 5  # Number of consecutive blocks to compare


def load_audio_hashes(csv_path):
    audios = {}
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            video = row["video"]
            fingerprint = np.array([float(x) for x in row["fingerprint"].split(",")])
            if video not in audios:
                audios[video] = []
            audios[video].append(fingerprint)
    return audios

def compute_sliding_fingerprint_distance(seq1, seq2):
    """
    Compare two audio/video fingerprint sequences with a sliding window.
    Handles short sequences safely and avoids junk indices.
    Returns the minimum cosine distance and the indices in seq1 and seq2.
    """
    len1 = len(seq1)
    len2 = len(seq2)

    # If either sequence is too short, compare raw frames directly
    if len1 == 0 or len2 == 0:
        return None  # Nothing to compare
    window_size = min(SLIDING_WINDOW_SIZE, len1, len2)

    min_diff = float("inf")
    min_i, min_j = None, None

    for i in range(len1 - window_size + 1):
        window1 = np.mean(seq1[i:i+window_size], axis=0)
        for j in range(len2 - window_size + 1):
            window2 = np.mean(seq2[j:j+window_size], axis=0)
            diff = cosine(window1, window2)

            if diff < min_diff:
                min_diff = diff
                min_i, min_j = i, j

    # If no valid comparison was found, return None
    if min_i is None or min_j is None:
        return None

    # Round distance to 10 decimals
    min_diff = round(min_diff, 10)
    return min_diff, min_i, min_j


def compute_audio_metrics(target_hashes, other_hashes, close_threshold=close_threshold):
    result = compute_sliding_fingerprint_distance(target_hashes, other_hashes)
    if result is None:
        return None

    min_diff, min_target_frame, min_other_frame = result

    # Compute distances for all sliding positions
    diffs = []
    len1 = len(target_hashes)
    len2 = len(other_hashes)
    for i in range(len1 - SLIDING_WINDOW_SIZE + 1):
        window1 = np.mean(target_hashes[i:i+SLIDING_WINDOW_SIZE], axis=0)
        for j in range(len2 - SLIDING_WINDOW_SIZE + 1):
            window2 = np.mean(other_hashes[j:j+SLIDING_WINDOW_SIZE], axis=0)
            diffs.append(cosine(window1, window2))

    max_diff = max(diffs)
    avg_diff = sum(diffs) / len(diffs)
    diff_range = max_diff - min_diff
    close_matches = sum(1 for d in diffs if d < close_threshold)
    percent_close = close_matches / len(diffs)

    return {
        "min_diff": round(min_diff, 10),
        "min_target_frame": min_target_frame,
        "min_other_frame": min_other_frame,
        "max_diff": round(max_diff, 10),
        "range": round(diff_range, 10),
        "avg_diff": round(avg_diff, 10),
        "percent_close_under_threshold": round(percent_close, 10)
    }


def compare_all(target_video_path, target_hashes, comparison_videos):
    results = []
    for video, hashes in comparison_videos.items():
        start_time = time.time()
        metrics = compute_audio_metrics(target_hashes, hashes)
        end_time = time.time()
        comparison_time = round(end_time - start_time, 10)

        if metrics:
            metrics["video"] = video
            metrics["target_video_path"] = target_video_path
            metrics["comparison_seconds"] = comparison_time
            results.append(metrics)
    return results


def save_metrics(results, output_csv):
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = [
            "target_video_path",
            "video",
            "min_diff",
            "min_target_frame",
            "min_other_frame",
            "max_diff",
            "range",
            "avg_diff",
            "percent_close_under_threshold",
            "comparison_seconds"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    if len(sys.argv) < 2:
        print("Usage: python audio_metrics.py <target_video_name>")
        return

    target_video = sys.argv[1]

    target_videos = load_audio_hashes(TARGET_CSV)
    comparison_videos = load_audio_hashes(COMPARISON_CSV)

    if target_video not in target_videos:
        print(f"Target video '{target_video}' not found in {TARGET_CSV}.")
        return

    print(f"Comparing audio of target video '{target_video}' against {len(comparison_videos)} videos...")

    target_hashes = target_videos[target_video]
    results = compare_all(target_video_path=target_video, target_hashes=target_hashes, comparison_videos=comparison_videos)

    results.sort(key=lambda x: x["min_diff"])
    save_metrics(results, OUTPUT_CSV)
    print(f"Done. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()