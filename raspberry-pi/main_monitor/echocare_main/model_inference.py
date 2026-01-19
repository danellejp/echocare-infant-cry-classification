"""
EchoCare Model Inference
Handles detection and classification models
"""

import tflite_runtime.interpreter as tflite
from config import *

class CryDetector:
    """Cry detection and classification using TFLite models"""
    
    def __init__(self):
        """Load TFLite models"""
        # Detection model
        self.detection_model = tflite.Interpreter(model_path=detection_model_path)
        self.detection_model.allocate_tensors()
        self.det_input = self.detection_model.get_input_details()[0]
        self.det_output = self.detection_model.get_output_details()[0]
        
        # Classification model
        self.classification_model = tflite.Interpreter(model_path=classification_model_path)
        self.classification_model.allocate_tensors()
        self.cls_input = self.classification_model.get_input_details()[0]
        self.cls_output = self.classification_model.get_output_details()[0]
    
    def detect(self, preprocessed_audio):
        """Run detection model"""
        self.detection_model.set_tensor(self.det_input['index'], preprocessed_audio)
        self.detection_model.invoke()
        result = self.detection_model.get_tensor(self.det_output['index'])
        return float(result[0][0])
    
    def classify(self, preprocessed_audio):
        """Run classification model"""
        self.classification_model.set_tensor(self.cls_input['index'], preprocessed_audio)
        self.classification_model.invoke()
        result = self.classification_model.get_tensor(self.cls_output['index'])
        return float(result[0][0])
    
    def process_cry(self, classification_score):
        """Determine cry type from classification score"""
        if classification_score >= classification_threshold:
            cry_type = cry_labels[1] if classification_score >= 0.5 else cry_labels[0]
            confidence = classification_score if classification_score >= 0.5 else (1 - classification_score)
        else:
            cry_type = "Normal"
            confidence = classification_score
        
        return cry_type, confidence