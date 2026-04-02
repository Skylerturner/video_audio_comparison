import os
import csv
import uuid
import time
import librosa
import numpy as np
from pydub import AudioSegment

# Config
CSV_PATH = "all_audio_hashes.csv"
FOLDERS_TO_PROCESS = [
    "downloads",
    "processed/reels_processed",
    "processed/shorts_processed"
]

SAMPLE_RATE = 44100  # Standardize audio sampling
BLOCK_LENGTH_SEC = 1.0  # 1-second blocks for fingerprints


def extract_audio(video_path, temp_audio_path):
    """
    Extract audio and convert to mono wav using pydub
    """
    audio = AudioSegment.from_file(video_path)
    audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
    audio.export(temp_audio_path, format="wav")


def compute_fingerprints(audio_path, block_length_sec=BLOCK_LENGTH_SEC):
    """
    Compute MFCC-based fingerprints per block
    """
    y, sr = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    block_length = int(block_length_sec * sr)
    fingerprints = []

    for start in range(0, len(y), block_length):
        end = min(start + block_length, len(y))
        block = y[start:end]
        if len(block) == 0:
            continue
        mfcc = librosa.feature.mfcc(y=block, sr=sr, n_mfcc=20)
        fingerprint = np.mean(mfcc.T, axis=0)  # Average over time
        fingerprints.append(fingerprint)

    return fingerprints


def save_fingerprints_to_csv(video_path, fingerprints, processing_time, csv_path=CSV_PATH):
    video_name = os.path.basename(video_path)
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['video', 'block', 'fingerprint', 'processing_seconds'])

        for i, fp in enumerate(fingerprints):
            fp_str = ",".join([f"{x:.6f}" for x in fp])
            writer.writerow([video_name, i, fp_str, processing_time])


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
            print(f"Processing audio for: {video_path}")

            unique_id = str(uuid.uuid4())
            temp_audio_path = f"./temp_audio_{unique_id}.wav"

            start_time = time.time()
            extract_audio(video_path, temp_audio_path)
            fingerprints = compute_fingerprints(temp_audio_path)
            end_time = time.time()

            processing_time = round(end_time - start_time, 3)
            save_fingerprints_to_csv(video_path, fingerprints, processing_time)

            os.remove(temp_audio_path)
            print(f"Saved audio fingerprints for {file_name}, processed in {processing_time} seconds")


if __name__ == "__main__":
    main()