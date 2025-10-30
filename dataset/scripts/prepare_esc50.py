"""
ESC-50 Dataset Preparation:

- Reserves 10 test samples from each of the 10 selected categories (saves metadata only)
- Processes 24 training samples per category (1200 segments)
- Processes 6 validation samples per category (300 segments)
- Saves to datasets/processed/cry_detection/train/non-cry/ and validate/non-cry/

"""

import pandas as pd # reading/writing CSV files and manipulating metadata
import numpy as np # numerical operations on audio arrays
import librosa # loading and resampling audio files
import soundfile as sf # saving segmented audio files as .wav
from pathlib import Path # cross-platform file path handling (Windows compatible)

raw_esc50_audio = Path("C:/Users/danel/FYP/ESC-50/audio")
raw_esc50_meta = Path("C:/Users/danel/FYP/ESC-50/meta/esc50.csv")

output_audio_dir = Path("dataset/processed/cry_detection/train/non-cry") # outputs the actual audios as .wav files
output_val_dir = Path("dataset/processed/cry_detection/validate/non-cry") # outputs the validation audios as .wav files
output_metadata_dir = Path("dataset/processed/cry_detection/test/non-cry") # outputs the test metadata CSV file

selected_categories = [
    'washing_machine', 'vacuum_cleaner', 'sneezing', 'coughing', 'footsteps',
    'laughing', 'snoring', 'dog', 'door_wood_knock', 'toilet_flush'
]

target_sr = 16000  # 16kHz
segment_duration = 1.0  # 1 second
test_samples_per_category = 10
train_samples_per_category = 24
val_samples_per_category = 6

def normalise_audio(audio):
    """Normalising audio to [-1, 1] range for consistent volume across all files"""
   
   # find the loudest point: convert to positive values, then get maximum
    max_val = np.abs(audio).max()
    if max_val > 0: # only normalise if there's actual sound
        audio = audio / max_val # scale audio so the loudest point becomes 1.0
        print(f"Normalized audio")
    else:
        print(f"Audio was silent, skipping normalisation")
    return audio



def segment_audio(audio, sample_rate, segment_duration=1.0):
    """Segment audio into 1-second clips for consistent input size"""

    # calculate how many samples are in 1 second
    segment_length = int(segment_duration * sample_rate)

    # calculate how many full segments can be made
    num_segments = len(audio) // segment_length

    # extract each 1-second segment
    segments = []
    for i in range(num_segments):
        start = i * segment_length
        end = start + segment_length
        segments.append(audio[start:end])
    
    print(f"Segmented into {num_segments} clips of {segment_duration}s each")
    
    return segments


def process_file(input_path, output_dir, filename_prefix):
    """Load, resample, normalise, segment, and save training file"""

    # load and resample to 16kHz
    audio, sr = librosa.load(input_path, sr=target_sr, mono=True)
    print(f"Resampled audio from {sr}Hz to {target_sr}Hz")

    # normalise
    audio = normalise_audio(audio)
    
    # segment into 1-second clips
    segments = segment_audio(audio, target_sr, segment_duration)
    
    # save each segment as a separate .wav file
    for idx, segment in enumerate(segments):
        output_path = output_dir / f"{filename_prefix}_seg{idx:02d}.wav"
        sf.write(output_path, segment, target_sr)
    
    return len(segments)


def main():
    """ splits data into train/validate/test and processes files """

    # load metadata
    df = pd.read_csv(raw_esc50_meta)

    # keep only rows where category is in 10 selected categories
    df = df[df['category'].isin(selected_categories)]

    # split into train/test sets
    test_samples = [] # 10 samples per category
    train_samples = [] # 24 samples per category
    val_samples = []   # 6 samples per category

    # loop through each of the 10 categories
    for category in selected_categories:
        # get all samples for this category (40 samples)
        category_df = df[df['category'] == category]

        # split: first 10 test, next 24 train, last 6 validate
        test_cat = category_df.head(test_samples_per_category)  # 0-9
        train_cat = category_df.iloc[test_samples_per_category:test_samples_per_category + train_samples_per_category]  # 10-33
        val_cat = category_df.iloc[test_samples_per_category + train_samples_per_category:]  # 34-39
        
        # add to sets
        test_samples.append(test_cat)
        train_samples.append(train_cat)
        val_samples.append(val_cat)
        
    # combine all categories back into single DataFrames
    test_df = pd.concat(test_samples, ignore_index=True) # 100 test samples
    train_df = pd.concat(train_samples, ignore_index=True) # 240 training samples
    val_df = pd.concat(val_samples, ignore_index=True) # 60 validation samples

    # save test metadata only
    test_csv_path = output_metadata_dir / "esc50_test_reserved.csv"
    test_df.to_csv(test_csv_path, index=False)
    print(f"\nSaved test metadata: {test_csv_path}")

    # process training files only
    print(f"Processing {len(train_df)} training files:")
    
    total_segments = 0 # counter for all segments created
    
    # loop through each training file
    for idx, row in train_df.iterrows():

        # construct input path and filename prefix
        input_path = raw_esc50_audio / row['filename']
        filename_prefix = f"{row['category']}_{Path(row['filename']).stem}"

        # process and save segments
        num_segments = process_file(input_path, output_audio_dir, filename_prefix)
        total_segments += num_segments

    # process validation files only
    print(f"Processing {len(val_df)} validation files:")
    total_val_segments = 0
    
    for idx, row in val_df.iterrows():
        input_path = raw_esc50_audio / row['filename']
        filename_prefix = f"{row['category']}_{Path(row['filename']).stem}"
        
        num_segments = process_file(input_path, output_val_dir, filename_prefix)
        total_val_segments += num_segments
    
    print("Done")

if __name__ == "__main__":
    main()