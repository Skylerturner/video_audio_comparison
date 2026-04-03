import csv
import os
import imagehash
import numpy as np

def save_hashes_to_csv(video_path, hashes, processing_time, csv_path):
    video_name = os.path.basename(video_path)
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['video', 'frame', 'phash', 'processing_seconds'])
        for i, h in enumerate(hashes):
            writer.writerow([video_name, i, str(h), processing_time])

def save_fingerprints_to_csv(video_path, fingerprints, processing_time, csv_path):
    video_name = os.path.basename(video_path)
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['video', 'block', 'fingerprint', 'processing_seconds'])
        for i, fp in enumerate(fingerprints):
            fp_str = ",".join([f"{x:.6f}" for x in fp])
            writer.writerow([video_name, i, fp_str, processing_time])

def load_hashes(csv_path):
    videos = {}
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            video = row["video"]
            hash_obj = imagehash.hex_to_hash(row["phash"])
            if video not in videos:
                videos[video] = []
            videos[video].append(hash_obj)
    return videos

def load_fingerprints(csv_path):
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