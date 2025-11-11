"""
Baby Chillanto Dataset Preparation for CRY CLASSIFICATION:

Uses ONLY hungry and pain cry types
Splits 70/15/15 into train/validate/test
Resamples to 16kHz
"""

import librosa
import soundfile as sf
from pathlib import Path
from sklearn.model_selection import train_test_split

# Paths
raw_base = Path("C:/Users/danel/FYP/baby-chillanto")
processed_base = Path("dataset/processed/cry_classification")

# Cry folders (only hungry and pain for classification)
cry_folders = {
    'hungry': raw_base / 'hungry' / '1 seg',
    'pain': raw_base / 'pain' / '1 seg'
}

# Output directories
output_dirs = {
    'train': {'hungry': processed_base / "train" / "hungry",
              'pain': processed_base / "train" / "pain"},
    'val': {'hungry': processed_base / "validate" / "hungry",
            'pain': processed_base / "validate" / "pain"},
    'test': {'hungry': processed_base / "test" / "hungry",
             'pain': processed_base / "test" / "pain"}
}

TARGET_SR = 16000

def process_file(input_path, output_dir, filename_prefix):
    """Load, resample, and save audio file"""
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
    print("Baby Chillanto - CRY CLASSIFICATION")
    
    # Load files
    all_files = load_files_from_folders(cry_folders)
    file_paths = [item[0] for item in all_files]
    categories = [item[1] for item in all_files]
    
    # Show distribution
    print(f"\nTotal files: {len(all_files)}")
    hungry_count = categories.count('hungry')
    pain_count = categories.count('pain')
    print(f"  Hungry: {hungry_count}")
    print(f"  Pain: {pain_count}")
    
    # Split data (70/15/15, stratified)
    print("\nSplitting data...")
    train_files, temp_files, train_cats, temp_cats = train_test_split(
        file_paths, categories,
        test_size=0.3,
        stratify=categories,
        random_state=42
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
        'train': (train_files, train_cats),
        'val': (val_files, val_cats),
        'test': (test_files, test_cats)
    }
    
    for split_name, (files, cats) in splits.items():
        print(f"\nProcessing {split_name.upper()}: {len(files)} samples...")
        
        counts = {'hungry': 0, 'pain': 0}
        
        for file_path, category in zip(files, cats):
            filename_prefix = f"{category}_{file_path.stem}"
            output_dir = output_dirs[split_name][category]
            
            success = process_file(file_path, output_dir, filename_prefix)
            counts[category] += success
        
        print(f"Hungry: {counts['hungry']}, Pain: {counts['pain']}")
    
    print("CompletedCRY CLASSIFICATION DATA")

if __name__ == "__main__":
    main()