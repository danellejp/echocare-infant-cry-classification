#!/usr/bin/env python3
"""
Test TFLite Model Inference on Raspberry Pi
"""

import time
import numpy as np
import tensorflow as tf

print("TFLite Model Inference Test - EchoCare")

# Load models
print("\nLoading models...")

detection_model = tf.lite.Interpreter(
    model_path="/home/danellepi/echocare/models/detection_model.tflite"
)
detection_model.allocate_tensors()
print("Detection model loaded")

classification_model = tf.lite.Interpreter(
    model_path="/home/danellepi/echocare/models/classification_model.tflite"
)
classification_model.allocate_tensors()
print("Classification model loaded")

# Get input/output details
det_input = detection_model.get_input_details()[0]
det_output = detection_model.get_output_details()[0]

cls_input = classification_model.get_input_details()[0]
cls_output = classification_model.get_output_details()[0]

print(f"\nDetection Model:")
print(f"Input: {det_input['shape']}")
print(f"Output: {det_output['shape']}")

print(f"\nClassification Model:")
print(f"Input: {cls_input['shape']}")
print(f"Output: {cls_output['shape']}")

# Test with dummy data
print(f"\nTesting inference with dummy data...")

dummy_detection = np.random.randn(*det_input['shape']).astype(np.float32)
dummy_classification = np.random.randn(*cls_input['shape']).astype(np.float32)

# Test detection
print(f"\nDetection inference...")
start = time.time()
detection_model.set_tensor(det_input['index'], dummy_detection)
detection_model.invoke()
det_result = detection_model.get_tensor(det_output['index'])
det_time = (time.time() - start) * 1000

print(f"Time: {det_time:.2f} ms")
print(f"Output: {det_result}")

# Test classification
print(f"\nClassification inference...")
start = time.time()
classification_model.set_tensor(cls_input['index'], dummy_classification)
classification_model.invoke()
cls_result = classification_model.get_tensor(cls_output['index'])
cls_time = (time.time() - start) * 1000

print(f"Time: {cls_time:.2f} ms")
print(f"Output: {cls_result}")

print(f"TOTAL INFERENCE TIME: {det_time + cls_time:.2f} ms")

if (det_time + cls_time) < 500:
    print("Fast enough for real-time cry detection")
elif (det_time + cls_time) < 1000:
    print("Acceptable performance")
else:
    print("Slower than ideal - but should still work")