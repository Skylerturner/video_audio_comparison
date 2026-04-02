import csv
import imagehash
import sys
import time

TARGET_CSV = "all_resize_hashes.csv"         # CSV containing the target video
COMPARISON_CSV = "all_resize_hashes_1fps.csv"  # CSV containing the videos to compare against
OUTPUT_CSV = "comparison_metrics_resize_allv1_kernel_scan.csv"
close_threshold = 10  # Adjust as needed for "close" matches


def load_hashes(csv_path):
    videos = {}
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            video = row["video"]
            hash_str = row["phash"]
            hash_obj = imagehash.hex_to_hash(hash_str)
            if video not in videos:
                videos[video] = []
            videos[video].append(hash_obj)
    return videos


def compute_metrics_kernel(target_hashes, other_hashes, close_threshold=close_threshold):
    """
    Kernel scanning: for each frame in other_hashes, compare only to the
    proportional window in target_hashes
    """
    diffs = []
    global_min_diff = sys.maxsize
    min_target_frame = None
    min_other_frame = None

    N = len(target_hashes)
    M = len(other_hashes)
    window_size = max(1, N // M)  # ensure at least 1 frame per window

    for j, h2 in enumerate(other_hashes):
        start_idx = j * window_size
        end_idx = min((j + 1) * window_size, N)
        min_diff_for_frame = sys.maxsize
        best_target_frame = None

        for i in range(start_idx, end_idx):
            h1 = target_hashes[i]
            diff = abs(h1 - h2)

            if diff < min_diff_for_frame:
                min_diff_for_frame = diff
                best_target_frame = i

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
    diff_range = max_diff - min_diff
    close_matches = sum(1 for d in diffs if d < close_threshold)
    percent_close = close_matches / len(diffs)

    return {
        "min_diff": min_diff,
        "min_target_frame": min_target_frame,
        "min_other_frame": min_other_frame,
        "max_diff": max_diff,
        "range": diff_range,
        "avg_diff": avg_diff,
        "percent_close_under_10": percent_close
    }


def compare_all(target_video_path, target_hashes, comparison_videos):
    results = []

    for video, hashes in comparison_videos.items():
        start_time = time.time()
        metrics = compute_metrics_kernel(target_hashes, hashes)
        end_time = time.time()
        comparison_time = round(end_time - start_time, 6)

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
            "percent_close_under_10",
            "comparison_seconds"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    if len(sys.argv) < 2:
        print("Usage: python phash_kernel_metrics.py <target_video_name>")
        return

    target_video = sys.argv[1]

    # Load hashes
    target_videos = load_hashes(TARGET_CSV)
    comparison_videos = load_hashes(COMPARISON_CSV)

    if target_video not in target_videos:
        print(f"Target video '{target_video}' not found in {TARGET_CSV}.")
        return

    print(f"Comparing target video '{target_video}' against {len(comparison_videos)} videos using kernel scan...")

    target_hashes = target_videos[target_video]
    results = compare_all(target_video_path=target_video, target_hashes=target_hashes, comparison_videos=comparison_videos)

    # Sort by strongest similarity (lowest min_diff first)
    results.sort(key=lambda x: x["min_diff"])

    save_metrics(results, OUTPUT_CSV)
    print(f"Done. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()