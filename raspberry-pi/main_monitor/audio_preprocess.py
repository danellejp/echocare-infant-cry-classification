"""
EchoCare Audio Processor
Handles audio capture and preprocessing
"""

import numpy as np
import cv2
import librosa
import pyaudio
from config import *


class AudioProcessor:
    """Audio capture and preprocessing"""
    
    def __init__(self):
        """Initialize PyAudio"""
        self.p = pyaudio.PyAudio()
    
    def capture(self):
        """Capture 1 second of audio"""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk
        )
        
        frames = []
        for _ in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        # Convert to numpy array
        audio = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio = audio.astype(np.float32) / 32768.0 # Normalize to [-1, 1]
        
        return audio
    
    
    def preprocess(self, audio, mean, std):
        """Preprocess audio for model input"""

        # Ensure correct length
        target_length = int(sample_rate * duration)
        if len(audio) < target_length:
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            audio = audio[:target_length]
        
        # Mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sample_rate,
            n_mels=n_mels,
            n_fft=n_fft,
            hop_length=hop_length
        )
        
        # Convert to dB
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec_normalized = (mel_spec_db - mean) / std
        
        # Prepare for MobileNetV2. Add channel dimension if needed
        if len(mel_spec_normalized.shape) == 2:
            mel_spec_normalized = np.expand_dims(mel_spec_normalized, axis=-1)
        
        # Resize to MobileNetV2's expected input size (224x224)
        resized = cv2.resize(mel_spec_normalized, target_size)
        
        # Ensure channel dimension exists after resize
        if len(resized.shape) == 2:
            resized = np.expand_dims(resized, axis=-1)
        
        # Convert grayscale (1 channel) to RGB (3 channels)
        if resized.shape[-1] == 1:
            resized = np.repeat(resized, 3, axis=-1)
        
        # Add batch dimension and convert to float32
        resized = np.expand_dims(resized, axis=0).astype(np.float32)
        
        return resized
    
    
    def terminate(self):
        """Terminate PyAudio"""
        self.p.terminate()