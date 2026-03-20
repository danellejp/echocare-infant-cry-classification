"""
Shared test fixtures for EchoCare backend tests.

Provides:
    - Temporary test database (auto-cleaned after each test)
    - Sample cry event data
    - FastAPI test client
"""

import pytest
import os
import sys
import tempfile

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from database import CryDatabase


@pytest.fixture
def test_db():
    """
    Create a temporary test database.
    
    Uses a temp file so tests don't affect the real database.
    Automatically cleaned up after each test.
    """
    # Create temp file for test database
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    # Create database instance
    db = CryDatabase(temp_path)
    
    yield db
    
    # Cleanup
    db.close()
    os.unlink(temp_path)


@pytest.fixture
def populated_db(test_db):
    """
    Test database pre-populated with sample cry events.
    
    Contains:
        - 3 Hungry events
        - 2 Pain events  
        - 1 Normal event
    All with realistic confidence scores and sensor data.
    """
    test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, 48.0)
    test_db.insert_cry_event("Hungry", 0.90, 0.78, 22.3, 47.5)
    test_db.insert_cry_event("Hungry", 0.95, 0.88, 22.8, 49.0)
    test_db.insert_cry_event("Pain", 0.88, 0.82, 23.1, 44.8)
    test_db.insert_cry_event("Pain", 0.91, 0.79, 23.5, 45.2)
    test_db.insert_cry_event("Normal", 0.87, 0.65, 22.0, 50.0)
    
    return test_db


@pytest.fixture
def sample_event():
    """
    A single sample cry event dictionary for testing.
    """
    return {
        "cry_type": "Hungry",
        "detection_conf": 0.92,
        "class_conf": 0.85,
        "temperature": 22.5,
        "humidity": 48.0
    }