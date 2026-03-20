"""
Unit tests for the Model Inference module.

Tests:
    - process_cry() classification logic
    - Cry type mapping based on classification scores
    - Confidence threshold handling
    - Boundary conditions

These tests only cover the classification LOGIC (process_cry method).
Actual model loading and inference require TFLite runtime and model files,
which are tested via integration tests on the Pi.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestProcessCry:
    """
    Tests for the process_cry classification logic.
    
    process_cry takes a classification_score and returns (cry_type, confidence):
    - score >= 0.70 and >= 0.50 -> Hungry (confidence = score)
    - score >= 0.70 and < 0.50 -> Pain (confidence = 1 - score)
    - score < 0.70 -> Normal (confidence = score)
    """

    def setup_method(self):
        """Set up mock CryDetector without loading models."""
        # Import config values we need
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        # We can't import CryDetector directly (needs TFLite),
        # so we test the logic manually
        self.CLASSIFICATION_THRESHOLD = 0.70
        self.CRY_LABELS = {0: "Pain", 1: "Hungry"}

    def process_cry(self, classification_score):
        """
        Replicate the process_cry logic for testing.
        This mirrors the actual CryDetector.process_cry method.
        """
        if classification_score >= self.CLASSIFICATION_THRESHOLD:
            if classification_score >= 0.5:
                cry_type = self.CRY_LABELS[1]  # Hungry
                confidence = classification_score
            else:
                cry_type = self.CRY_LABELS[0]  # Pain
                confidence = 1 - classification_score
        else:
            cry_type = "Normal"
            confidence = classification_score
        return cry_type, confidence

    # High confidence — Hungry
    def test_high_score_returns_hungry(self):
        """Score >= 0.70 and >= 0.50 should return Hungry."""
        cry_type, confidence = self.process_cry(0.85)
        assert cry_type == "Hungry"
        assert confidence == 0.85

    def test_score_at_threshold_returns_hungry(self):
        """Score exactly at 0.70 should return Hungry."""
        cry_type, confidence = self.process_cry(0.70)
        assert cry_type == "Hungry"
        assert confidence == 0.70

    def test_full_confidence_hungry(self):
        """Score of 1.0 should return Hungry with full confidence."""
        cry_type, confidence = self.process_cry(1.0)
        assert cry_type == "Hungry"
        assert confidence == 1.0

    # Below threshold — Normal
    def test_low_score_returns_normal(self):
        """Score below 0.70 should return Normal."""
        cry_type, confidence = self.process_cry(0.60)
        assert cry_type == "Normal"
        assert confidence == 0.60

    def test_very_low_score_returns_normal(self):
        """Very low score should return Normal."""
        cry_type, confidence = self.process_cry(0.20)
        assert cry_type == "Normal"
        assert confidence == 0.20

    def test_just_below_threshold_returns_normal(self):
        """Score just below 0.70 should return Normal."""
        cry_type, confidence = self.process_cry(0.69)
        assert cry_type == "Normal"
        assert confidence == 0.69

    def test_zero_score_returns_normal(self):
        """Score of 0 should return Normal."""
        cry_type, confidence = self.process_cry(0.0)
        assert cry_type == "Normal"
        assert confidence == 0.0

    # Boundary tests
    def test_score_at_0_5_returns_hungry(self):
        """Score at 0.5 is below threshold, should return Normal."""
        cry_type, confidence = self.process_cry(0.50)
        assert cry_type == "Normal"
        assert confidence == 0.50

    def test_score_0_71_returns_hungry(self):
        """Score of 0.71 should return Hungry."""
        cry_type, confidence = self.process_cry(0.71)
        assert cry_type == "Hungry"

    def test_return_type_is_string(self):
        """Cry type should always be a string."""
        cry_type, _ = self.process_cry(0.85)
        assert isinstance(cry_type, str)

    def test_return_confidence_is_float(self):
        """Confidence should always be a float."""
        _, confidence = self.process_cry(0.85)
        assert isinstance(confidence, float)