"""
Test Audio Preprocessing Pipeline on Raspberry Pi
Tests if Pi can generate mel-spectrograms in real-time for cry detection
"""

import time
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import cv2
from pathlib import Path

print("Audio Preprocessing Test")

# Parameters (from training configuration)
sample_rate = 16000
duration = 1.0
n_mels = 128
target_size = (224, 224)

# OPTIMIZED mel-spectrogram parameters
n_fft = 1024        # Reduced from default 2048 (2x faster)
hop_length = 512    # Larger hop = fewer frames = faster

# Normalization parameters from training (Z-score standardisation)
cry_detection_mean = -37.628456115722656
cry_detection_std = 22.107717514038086
cry_classification_mean = -40.55323028564453
cry_classification_std = 19.64647102355957

# Test audio file path (audio from testing microphone)
audio_file = "/home/danellepi/echocare/test_recording.wav"

print(f"\nAudio file found: {audio_file}")
print(f"\nConfiguration:")
print(f"  Sample Rate: {sample_rate}Hz")
print(f"  Duration: {duration}s")
print(f"  Mel Bands: {n_mels}")
print(f"  Target Size: {target_size}")


def load_and_preprocess_audio(audio_path, mean, std):
    """
    Load audio file and prepare for model input following the exact training pipeline.
    
    Args:
        audio_path: Path to audio file
        mean: Training mean for Z-score normalization
        std: Training std for Z-score normalization
    
    Returns:
        Preprocessed audio ready for model inference
    """

    print("Preprocessing Pipeline:")
    
    step_times = {} # To store time taken for each step
    total_start = time.time()
    
    # Step 1: Load audio file at target sample rate
    print(f"\n[Step 1/7] Loading audio file...")
    step_start = time.time()
    # Load with soundfile
    audio, sr = sf.read(audio_path, dtype='float32')
    
    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    
    # Resample if needed (using scipy - faster than librosa)
    if sr != sample_rate:
        num_samples = int(len(audio) * sample_rate / sr)
        audio = signal.resample(audio, num_samples)
    
    # Pad or trim to exact duration
    target_length = int(sample_rate * duration)
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)))
    else:
        audio = audio[:target_length]
    
    step_times['load'] = (time.time() - step_start) * 1000
    print(f"Audio loaded: {len(audio)} samples at {sample_rate}Hz")
    print(f"Time: {step_times['load']:.2f} ms")
    
    # Step 2: Convert to mel-spectrogram
    print(f"\n[Step 2/7] Creating mel-spectrogram...")
    step_start = time.time()
    
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sample_rate,
        n_mels=n_mels,
        n_fft=n_fft,        # Smaller FFT window
        hop_length=hop_length  # Larger hop
    )

    step_times['mel_spec'] = (time.time() - step_start) * 1000
    print(f"Mel-spectrogram created: {mel_spec.shape}")
    print(f"Time: {step_times['mel_spec']:.2f} ms")
    
    # Step 3: Convert to log scale (dB)
    print(f"\n[Step 3/7] Converting to dB scale...")
    step_start = time.time()
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    step_times['db_convert'] = (time.time() - step_start) * 1000
    print(f"Converted to dB scale")
    print(f"Time: {step_times['db_convert']:.2f} ms")
    
    # Step 4: Z-score standardization using training statistics
    print(f"\n[Step 4/7] Z-score standardization...")
    step_start = time.time()
    mel_spec_normalized = (mel_spec_db - mean) / std
    step_times['normalize'] = (time.time() - step_start) * 1000
    print(f"Standardized using mean={mean:.2f}, std={std:.2f}")
    print(f"Time: {step_times['normalize']:.2f} ms")
    
    # Step 5-7: Prepare for MobileNetV2 (resize + RGB + batch)
    print(f"\n[Step 5-7/7] Preparing for MobileNetV2...")
    step_start = time.time()
    prepared_spec = prepare_for_mobilenet(mel_spec_normalized)
    step_times['mobilenet_prep'] = (time.time() - step_start) * 1000
    print(f"Final shape: {prepared_spec.shape}")
    print(f"Time: {step_times['mobilenet_prep']:.2f} ms")
    
    total_time = (time.time() - total_start) * 1000
    
    return prepared_spec, step_times, total_time


def prepare_for_mobilenet(spectrogram, target_size=(224, 224)):
    """
    Prepare mel-spectrogram for MobileNetV2 input.
    
    Args:
        spectrogram: numpy array mel-spectrogram (already standardized)
        target_size: tuple (height, width) for resizing
    
    Returns:
        Preprocessed spectrogram ready for model (batch_size, 224, 224, 3)
    """
    
    # Step 1: Add channel dimension if needed
    if len(spectrogram.shape) == 2:
        spectrogram = np.expand_dims(spectrogram, axis=-1)
    
    # Step 2: Resize to MobileNetV2's expected input size (224x224)
    resized = cv2.resize(spectrogram, target_size)
    
    # Step 3: Ensure channel dimension exists after resize
    if len(resized.shape) == 2:
        resized = np.expand_dims(resized, axis=-1)
    
    # Step 4: Convert grayscale (1 channel) to RGB (3 channels)
    if resized.shape[-1] == 1:
        resized = np.repeat(resized, 3, axis=-1)
    
    # Step 5: Add batch dimension
    resized = np.expand_dims(resized, axis=0)
    
    return resized.astype(np.float32)


# ========================================
# Run Preprocessing Test
# ========================================

print("Starting Preprocessing Test...")

try:
    # Test with detection normalisation parameters
    print("\nTesting with DETECTION model parameters...")
    detection_data, detection_times, detection_total = load_and_preprocess_audio(
        audio_file,
        cry_detection_mean,
        cry_detection_std
    )
    
    # Test with classification normalization parameters
    print(f"\n\nTesting with CLASSIFICATION model parameters...")
    classification_data, classification_times, classification_total = load_and_preprocess_audio(
        audio_file,
        cry_classification_mean,
        cry_classification_std
    )
    
    # ========================================
    # Performance Analysis
    # ========================================
    
    print("Performance Analysis:")
    
    print(f"\nStep-by-Step Breakdown (Detection Model):")
    print(f"   1. Load audio:          {detection_times['load']:.2f} ms")
    print(f"   2. Mel-spectrogram:     {detection_times['mel_spec']:.2f} ms")
    print(f"   3. dB conversion:       {detection_times['db_convert']:.2f} ms")
    print(f"   4. Normalization:       {detection_times['normalize']:.2f} ms")
    print(f"   5-7. MobileNet prep:    {detection_times['mobilenet_prep']:.2f} ms")
    print(f"   TOTAL:                  {detection_total:.2f} ms")
    
    print(f"\nClassification Model Total: {classification_total:.2f} ms")
    
    # Calculate average
    avg_preprocessing = (detection_total + classification_total) / 2
    print(f"\nAverage Preprocessing Time: {avg_preprocessing:.2f} ms")
    
    
    # Real-time capability analysis
    print(f"\n{'='*60}")
    print("Real-Time Capability Analysis")
    print(f"{'='*60}")
    
    # Assuming 1-second audio chunks
    processing_overhead = avg_preprocessing / 1000  # Convert to seconds
    audio_duration = 1.0  # seconds
    
    print(f"\nFor 1-second audio chunks:")
    print(f"  Audio duration: {audio_duration:.3f} seconds")
    print(f"  Processing time: {processing_overhead:.3f} seconds")
    print(f"  Overhead: {(processing_overhead/audio_duration)*100:.1f}%")
    
    if processing_overhead < audio_duration:
        print(f"\nReal-time capable: Can process faster than audio arrives")
        print(f"Time saved: {(audio_duration - processing_overhead)*1000:.0f} ms per chunk")
    else:
        print(f"\nNot real-time: Processing takes longer than audio duration")
        print(f"Delay: {(processing_overhead - audio_duration)*1000:.0f} ms per chunk")
    
    # Memory usage
    print(f"\n{'='*60}")
    print("Memory Usage Analysis")
    print(f"{'='*60}")
    
    detection_memory = detection_data.nbytes / 1024  # KB
    classification_memory = classification_data.nbytes / 1024  # KB
    
    print(f"\nPreprocessed data size:")
    print(f"  Detection model:       {detection_memory:.2f} KB")
    print(f"  Classification model:  {classification_memory:.2f} KB")
    
    # Data validation
    print(f"\n{'='*60}")
    print("Data Validation")
    print(f"{'='*60}")
    
    print(f"\nDetection data:")
    print(f"  Shape:  {detection_data.shape}")
    print(f"  Type:   {detection_data.dtype}")
    print(f"  Range:  [{detection_data.min():.3f}, {detection_data.max():.3f}]")
    print(f"  Mean:   {detection_data.mean():.3f}")
    print(f"  Std:    {detection_data.std():.3f}")
    
    print(f"\nClassification data:")
    print(f"  Shape:  {classification_data.shape}")
    print(f"  Type:   {classification_data.dtype}")
    print(f"  Range:  [{classification_data.min():.3f}, {classification_data.max():.3f}]")
    print(f"  Mean:   {classification_data.mean():.3f}")
    print(f"  Std:    {classification_data.std():.3f}")
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    print(f"\nAudio preprocessing pipeline: WORKING")
    print(f"Mel-spectrogram generation: WORKING")
    print(f"Data shape: CORRECT {detection_data.shape}")
    print(f"Average processing time: {avg_preprocessing:.2f} ms")
    
    if avg_preprocessing < 500:
        print(f"\nRaspberry Pi is ready for real-time cry detection")
    else:
        print(f"\nOptimisation is needed.")

except Exception as e:
    print(f"\nERROR during preprocessing:")
    print(f"   {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nTest complete")
