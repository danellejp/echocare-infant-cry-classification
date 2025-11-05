"""
Baby Chillanto Dataset preparation for cry classification:
Uses only hungry and pain cry types:

Splits 70/15/15 into train/validate/test
Resamples to 16kHz
Saves to datasets/processed/cry_classification/train/cry, validate/cry, test/cry
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from sklearn.model_selection import train_test_split

# Input path
raw_base = Path("C:/Users/danel/FYP/baby-chillanto")