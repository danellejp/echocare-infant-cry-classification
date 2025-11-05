"""
ESC-50 Dataset Preparation:

10 categories, each with 40 samples (total 400 samples):
- Splits 70/15/15 into train/validate/test at FILE level (before segmentation)
- Resamples to 16kHz
- Segments audio into 1-second clips
- Saves to datasets/processed/cry_detection/train/non-cry/, validate/non-cry/, and test/non-cry/
"""

import pandas as pd  # reading/writing CSV files and manipulating metadata
import numpy as np  # numerical operations on audio arrays
import librosa  # loading and resampling audio files
import soundfile as sf  # saving segmented audio files as .wav
from pathlib import Path  # cross-platform file path handling (Windows compatible)

# Input paths
raw_esc50_audio = Path("C:/Users/danel/FYP/ESC-50/audio")
raw_esc50_meta = Path("C:/Users/danel/FYP/ESC-50/meta/esc50.csv")

# Output paths
output_train_dir = Path("dataset/processed/cry_detection/train/non-cry")
output_val_dir = Path("dataset/processed/cry_detection/validate/non-cry")
output_test_dir = Path("dataset/processed/cry_detection/test/non-cry")

# Selected categories
selected_categories = [
    'washing_machine', 'vacuum_cleaner', 'sneezing', 'coughing', 'footsteps',
    'laughing', 'snoring', 'dog', 'door_wood_knock', 'toilet_flush'
]

# Settings
target_sr = 16000  # 16kHz sample rate
segment_duration = 1.0  # 1 second segments

# Split configuration (per category)
# Each category has 40 samples total
train_samples_per_category = 28  # 70% of 40
val_samples_per_category = 6     # 15% of 40
test_samples_per_category = 6    # 15% of 40


def segment_audio(audio, sample_rate, segment_duration=1.0):
    """
    Segment audio into fixed-length clips
    
    Args:
        audio: numpy array of audio samples
        sample_rate: sample rate in Hz
        segment_duration: length of each segment in seconds
    
    Returns:
        list of audio segments
    """
    # Calculate segment length in samples
    segment_length = int(segment_duration * sample_rate)
    
    # Calculate number of full segments
    num_segments = len(audio) // segment_length
    
    # Extract segments
    segments = []
    for i in range(num_segments):
        start = i * segment_length
        end = start + segment_length
        segments.append(audio[start:end])
    
    print(f"Segmented into {num_segments} clips of {segment_duration}s each")
    
    return segments


def process_file(input_path, output_dir, filename_prefix, target_sr=16000):
    """
    Load, resample, segment, and save audio file
    
    Args:
        input_path: path to input audio file
        output_dir: directory to save segments
        filename_prefix: prefix for output filenames
        target_sr: target sample rate
    
    Returns:
        number of segments created
    """
    # Step 1: Load and resample to 16kHz
    audio, sr = librosa.load(input_path, sr=target_sr, mono=True)
    
    # Step 2: Segment into 1-second clips
    segments = segment_audio(audio, target_sr, segment_duration=1.0)
    
    # Step 3: Save each segment as separate .wav file
    for idx, segment in enumerate(segments):
        output_path = output_dir / f"{filename_prefix}_seg{idx:02d}.wav"
        sf.write(output_path, segment, target_sr)
    
    return len(segments)


def main():
    """
    Split ESC-50 data into train/validate/test at FILE level,
    then process and segment each split separately
    """
    
    # Load metadata
    df = pd.read_csv(raw_esc50_meta)
    print(f"\nLoaded {len(df)} total samples from ESC-50")
    
    # Filter to selected categories only
    df = df[df['category'].isin(selected_categories)]
    print(f"Filtered to {len(df)} samples from {len(selected_categories)} categories")
    
    # Initialize split dataframes
    train_samples = []
    val_samples = []
    test_samples = []
    
    # Split each category separately to maintain balance
    print(f"\nSplitting each category (40 samples):")
    print(f"  Train: {train_samples_per_category} samples (70%)")
    print(f"  Validate: {val_samples_per_category} samples (15%)")
    print(f"  Test: {test_samples_per_category} samples (15%)")
    
    for category in selected_categories:
        # Get all samples for this category
        category_df = df[df['category'] == category]
        
        # Split: 28 train, 6 val, 6 test (70/15/15 split)
        train_cat = category_df.iloc[0:train_samples_per_category]
        val_cat = category_df.iloc[train_samples_per_category:train_samples_per_category + val_samples_per_category]
        test_cat = category_df.iloc[train_samples_per_category + val_samples_per_category:]
        
        # Add to respective lists
        train_samples.append(train_cat)
        val_samples.append(val_cat)
        test_samples.append(test_cat)
    
    # Combine all categories
    train_df = pd.concat(train_samples, ignore_index=True)  # 280 files
    val_df = pd.concat(val_samples, ignore_index=True)      # 60 files
    test_df = pd.concat(test_samples, ignore_index=True)    # 60 files
    
    print(f"\nFinal file counts:")
    print(f"  Train: {len(train_df)} files")
    print(f"  Validate: {len(val_df)} files")
    print(f"  Test: {len(test_df)} files")
    
    # process training files
    train_segment_count = 0
    for idx, row in train_df.iterrows():
        input_path = raw_esc50_audio / row['filename']
        filename_prefix = f"{row['category']}_{Path(row['filename']).stem}"
        
        num_segments = process_file(input_path, output_train_dir, filename_prefix, target_sr)
        train_segment_count += num_segments
    
    print(f"Training complete: {train_segment_count} segments created")
    
    # process validation files
    val_segment_count = 0
    for idx, row in val_df.iterrows():
        input_path = raw_esc50_audio / row['filename']
        filename_prefix = f"{row['category']}_{Path(row['filename']).stem}"
        
        num_segments = process_file(input_path, output_val_dir, filename_prefix, target_sr)
        val_segment_count += num_segments
    
    print(f"Validation complete: {val_segment_count} segments created")
    
    # process test files
    test_segment_count = 0
    for idx, row in test_df.iterrows():
        input_path = raw_esc50_audio / row['filename']
        filename_prefix = f"{row['category']}_{Path(row['filename']).stem}"
        
        num_segments = process_file(input_path, output_test_dir, filename_prefix, target_sr)
        test_segment_count += num_segments
    
    print(f"Test complete: {test_segment_count} segments created")
    
    print(f"Files processed:")
    print(f"  Train: {len(train_df)} files → {train_segment_count} segments")
    print(f"  Validate: {len(val_df)} files → {val_segment_count} segments")
    print(f"  Test: {len(test_df)} files → {test_segment_count} segments")
    print(f"\nTotal segments: {train_segment_count + val_segment_count + test_segment_count}")
    print(f"\nOutput directories:")
    print(f"  Train: {output_train_dir}")
    print(f"  Validate: {output_val_dir}")
    print(f"  Test: {output_test_dir}")

if __name__ == "__main__":
    main()