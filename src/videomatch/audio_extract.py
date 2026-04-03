import os
import uuid
import numpy as np
import librosa
from pydub import AudioSegment

SAMPLE_RATE = 44100
BLOCK_LENGTH_SEC = 1.0

def extract_audio_to_wav(video_path, temp_audio_path, sample_rate=SAMPLE_RATE):
    audio = AudioSegment.from_file(video_path)
    audio = audio.set_channels(1).set_frame_rate(sample_rate)
    audio.export(temp_audio_path, format="wav")

def compute_fingerprints(audio_path, sample_rate=SAMPLE_RATE, block_length_sec=BLOCK_LENGTH_SEC):
    y, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    block_length = int(block_length_sec * sr)
    fingerprints = []

    for start in range(0, len(y), block_length):
        end = min(start + block_length, len(y))
        block = y[start:end]
        if len(block) == 0:
            continue
        mfcc = librosa.feature.mfcc(y=block, sr=sr, n_mfcc=20)
        fingerprints.append(np.mean(mfcc.T, axis=0))

    return fingerprints

def extract_audio_fingerprints(video_path, sample_rate=SAMPLE_RATE, block_length_sec=BLOCK_LENGTH_SEC):
    unique_id = str(uuid.uuid4())
    temp_audio_path = f"./temp_audio_{unique_id}.wav"

    extract_audio_to_wav(video_path, temp_audio_path, sample_rate)
    fingerprints = compute_fingerprints(temp_audio_path, sample_rate, block_length_sec)

    os.remove(temp_audio_path)
    return fingerprints