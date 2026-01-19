"""
EchoCare Configuration
All settings in one place
"""
import pyaudio

# Audio configuration
sample_rate = 16000
duration = 1.0
chunk = 1024
format = pyaudio.paInt16
channels = 1

# Preprocessing configuration
n_mels = 128
n_fft = 1024
hop_length = 512
target_size = (224, 224)

# Normalization parameters from training (Z-score standardisation)
cry_detection_mean = -37.628456115722656
cry_detection_std = 22.107717514038086
cry_classification_mean = -40.55323028564453
cry_classification_std = 19.64647102355957

# Thresholds
detection_threshold = 0.85
classification_threshold = 0.70

# LED GPIO pins
clk_pin = 17
data_pin = 18

# LED colors for cry types
led_colours = {
    "Hungry": (0, 255, 0),      # Green for hungry cries
    "Pain": (255, 0, 0),  # Red for pain/discomfort cries
    "Normal": (0, 0, 255)        # Blue for normal cries
}

# Cry type labels
cry_labels = {
    0: "Pain",
    1: "Hungry"
}

# Model paths
detection_model_path = "/home/danellepi/echocare/models/detection_model.tflite"
classification_model_path = "/home/danellepi/echocare/models/classification_model.tflite"

# Database path
database_path = "/home/danellepi/echocare/echocare.db"