# video_audio_comparison

Research project exploring cheap and accurate video matching across different short-form platforms (YouTube Shorts, Instagram Reels, TikTok, etc.). The goal is to identify when the same source video has been uploaded across multiple platforms, potentially with minor edits, re-encoding, or platform-specific processing applied.

No conclusions have been finalized yet — see the `comparison/` notebooks for ongoing validation.

---

## Methods

### Visual Fingerprinting
Three visual fingerprinting approaches are compared:

- **pHash (Perceptual Hash)**: Applies a Discrete Cosine Transform to a grayscale frame and encodes the low-frequency coefficients into a compact hash. Similar frames produce similar hashes comparable via Hamming distance.
- **dHash (Difference Hash)**: Encodes the horizontal gradient between adjacent pixels in a resized grayscale frame. Captures edge and structural content, also compared via Hamming distance.
- **HSV Color Histogram**: Converts frames to HSV color space and computes normalized per-channel histograms. Captures color distribution rather than structure, compared via cosine distance.

Two extraction strategies for pHash are also compared:
- **Disk-based**: Frames are written to disk as JPGs and read back for hashing (original approach).
- **In-memory**: Frames are resized to a fixed resolution, cropped, and hashed entirely in memory without touching disk (improved approach).

### Audio Fingerprinting
- **Chromaprint**: The algorithm behind AcoustID. Analyzes chroma features (energy distribution across 12 pitch classes) and encodes them into a compact integer array comparable via normalized Hamming distance. More robust to compression and volume changes than MFCC-based approaches.

### Matching Pipelines
Four matching pipeline strategies are evaluated:
1. **Visual voting**: 2 of 3 visual methods must agree.
2. **Soft voting**: 2 of 4 methods (visual + audio) must agree.
3. **Hard filter — Audio gate**: Audio eliminates non-candidates, then 2 of 3 visual methods vote.
4. **Hard filter — pHash gate**: pHash eliminates non-candidates, then 2 of 3 remaining methods vote.

### Chunking Strategy
All fingerprints are computed on 4-second chunks with 1-second overlap between consecutive chunks, sampled at 5fps for visual and at a fixed sample rate for audio. This provides temporal coverage without excessive redundancy.

---

## Folder Structure

```
video_audio_comparison/
├── comparison/                  # Jupyter notebooks for method exploration and validation
│   ├── 01_phash_disk_vs_inmemory.ipynb
│   ├── 02_visual_comparison_methods.ipynb
│   ├── 03_audio_fingerprinting.ipynb
│   ├── 04_comparison_thresholds.ipynb
│   └── 05_filtering_pipelines.ipynb
├── src/
│   └── videomatch/              # Core reusable modules
│       ├── __init__.py
│       ├── video_extract.py     # Frame extraction (disk-based and in-memory)
│       ├── audio_extract.py     # Audio extraction and Chromaprint fingerprinting
│       ├── csv_storage.py       # Load and save hash/fingerprint CSVs
│       └── metrics.py           # Comparison algorithms (standard, kernel, audio)
├── scripts/                     # Entry point scripts (in progress)
├── reference/
│   └── phash.py                 # Original untouched reference implementation
├── data/                        # Local only — see Data section below
│   ├── downloads/
│   └── processed/
│       ├── reels_processed/
│       └── shorts_processed/
└── environment.yaml
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/video_audio_comparison.git
cd video_audio_comparison
```

### 2. Create and activate the conda environment
```bash
conda env create -f environment.yaml
conda activate videomatch
```

### 3. Launch the notebooks
```bash
cd comparison
jupyter notebook
```

---

## Data

Video files are not included in this repository due to their size. If you would like access to the dataset, please reach out directly.

The expected folder structure under `data/` is:
```
data/
├── downloads/           # Original downloaded source videos
└── processed/
    ├── reels_processed/ # Instagram Reels versions
    └── shorts_processed/ # YouTube Shorts versions
```