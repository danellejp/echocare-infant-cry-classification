"""
Baby Chillanto Dataset Preparation for CRY DETECTION:

Uses ALL cry types (hungry, pain, normal) as positive class
Splits 70/15/15 into train/validate/test
Resamples to 16kHz
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from sklearn.model_selection import train_test_split

# Paths
raw_base = Path("C:/Users/danel/FYP/baby-chillanto")
processed_base = Path("dataset/processed/cry_detection")

# Cry folders
cry_folders = {
    'hungry': raw_base / 'hungry' / '1 seg',
    'pain': raw_base / 'pain' / '1 seg',
    'normal': raw_base / 'normal' / '1 seg'
}

# Output directories
output_dirs = {
    'train': processed_base / "train" / "cry",
    'val': processed_base / "validate" / "cry",
    'test': processed_base / "test" / "cry"
}

TARGET_SR = 16000 # 16kHz sample rate


def process_file(input_path, output_dir, filename_prefix):
    """Load, resample and save audio file"""
    try:
        audio, _ = librosa.load(input_path, sr=TARGET_SR, mono=True)
        output_path = output_dir / f"{filename_prefix}.wav"
        sf.write(output_path, audio, TARGET_SR)
        return 1
    except Exception as e:
        print(f"Error: {input_path.name}: {e}")
        return 0


def load_files_from_folders(cry_folders):
    """Load all .wav files from category folders"""
    all_files = []
    
    for category, folder_path in cry_folders.items():
        wav_files = list(folder_path.glob("*.wav"))
        all_files.extend([(f, category) for f in wav_files])
        print(f"Found {len(wav_files)} {category} files")
    
    return all_files


def main():
    print("Baby Chillanto - CRY DETECTION")
    
    # Load files
    all_files = load_files_from_folders(cry_folders)
    file_paths = [item[0] for item in all_files]
    categories = [item[1] for item in all_files]
    
    print(f"\nTotal files: {len(all_files)}")
    for cat in ['hungry', 'pain', 'normal']:
        count = categories.count(cat)
        print(f"  {cat}: {count} ({count/len(categories)*100:.1f}%)")
    
    # Split data (stratified, reproducible)
    print("\nSplitting data (70/15/15)...")
    
    train_files, temp_files, train_cats, temp_cats = train_test_split(
        file_paths, categories,
        test_size=0.3,
        stratify=categories,
        random_state=42  # Reproducible split
    )
    
    val_files, test_files, val_cats, test_cats = train_test_split(
        temp_files, temp_cats,
        test_size=0.5,
        stratify=temp_cats,
        random_state=42
    )
    
    print(f"  Train: {len(train_files)} samples")
    print(f"  Val: {len(val_files)} samples")
    print(f"  Test: {len(test_files)} samples")
    
    # Process all splits
    splits = {
        'train': (train_files, train_cats, output_dirs['train']),
        'val': (val_files, val_cats, output_dirs['val']),
        'test': (test_files, test_cats, output_dirs['test'])
    }
    
    for split_name, (files, cats, output_dir) in splits.items():
        print(f"\nProcessing {split_name.upper()}: {len(files)} samples...")
        
        success = 0
        for file_path, category in zip(files, cats):
            filename_prefix = f"{category}_{file_path.stem}"
            success += process_file(file_path, output_dir, filename_prefix)
        
        print(f"Complete: {success}/{len(files)} processed")

    print("Done.")

if __name__ == "__main__":
    main()