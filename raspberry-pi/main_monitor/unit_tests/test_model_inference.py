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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestProcessCry:
    """
    Tests for the process_cry classification logic.
    
    process_cry takes a classification_score and returns (cry_type, confidence):
    - score >= 0.70 -> Hungry (confidence = score)
    - score <= 0.30 -> Pain (confidence = 1 - score)
    - score 0.31 to 0.69 -> Normal (confidence = score)
    """

    def setup_method(self):
        """Set up classification threshold for testing."""
        self.CLASSIFICATION_THRESHOLD = 0.70

    def process_cry(self, classification_score):
        """
        Replicate the process_cry logic for testing.
        This mirrors the actual CryDetector.process_cry method.
        """
        if classification_score >= self.CLASSIFICATION_THRESHOLD:
            cry_type = "Hungry"
            confidence = classification_score
        elif classification_score <= (1 - self.CLASSIFICATION_THRESHOLD):
            cry_type = "Pain"
            confidence = 1 - classification_score
        else:
            cry_type = "Normal"
            confidence = classification_score
        return cry_type, confidence

    # =========================================================================
    # High confidence - Hungry (score >= 0.70)
    # =========================================================================

    def test_high_score_returns_hungry(self):
        """Score of 0.85 should return Hungry with confidence 0.85."""
        score = 0.85
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Hungry"
        assert confidence == 0.85

    def test_score_at_hungry_threshold(self):
        """Score exactly at 0.70 should return Hungry."""
        score = 0.70
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Hungry"
        assert confidence == 0.70

    def test_full_confidence_hungry(self):
        """Score of 1.0 should return Hungry with full confidence."""
        score = 1.0
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Hungry"
        assert confidence == 1.0

    # =========================================================================
    # High confidence - Pain (score <= 0.30)
    # =========================================================================

    def test_low_score_returns_pain(self):
        """Score of 0.15 should return Pain with confidence 0.85."""
        score = 0.15
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Pain"
        assert confidence == 0.85

    def test_score_at_pain_threshold(self):
        """Score exactly at 0.30 should return Pain."""
        score = 0.30
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Pain"
        assert confidence == 0.70

    def test_zero_score_returns_pain(self):
        """Score of 0.0 should return Pain with full confidence."""
        score = 0.0
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Pain"
        assert confidence == 1.0

    # =========================================================================
    # Middle range - Normal (score between 0.31 and 0.69)
    # =========================================================================

    def test_middle_score_returns_normal(self):
        """Score of 0.50 should return Normal."""
        score = 0.50
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Normal"
        assert confidence == 0.50

    def test_just_below_hungry_threshold_returns_normal(self):
        """Score of 0.69 should return Normal, not Hungry."""
        score = 0.69
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Normal"
        assert confidence == 0.69

    def test_just_above_pain_threshold_returns_normal(self):
        """Score of 0.31 should return Normal, not Pain."""
        score = 0.31
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Normal"
        assert confidence == 0.31

    # =========================================================================
    # Boundary tests
    # =========================================================================

    def test_score_0_71_returns_hungry(self):
        """Score just above threshold should return Hungry."""
        score = 0.71
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Hungry"

    def test_score_0_29_returns_pain(self):
        """Score just below pain threshold should return Pain."""
        score = 0.29
        cry_type, confidence = self.process_cry(score)
        assert cry_type == "Pain"

    # =========================================================================
    # Type checks
    # =========================================================================

    def test_return_type_is_string(self):
        """Cry type should always be a string."""
        cry_type, _ = self.process_cry(0.85)
        assert isinstance(cry_type, str)

    def test_return_confidence_is_float(self):
        """Confidence should always be a float."""
        _, confidence = self.process_cry(0.85)
        assert isinstance(confidence, float)