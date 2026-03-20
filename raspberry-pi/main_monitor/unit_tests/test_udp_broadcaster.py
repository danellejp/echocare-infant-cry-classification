"""
Unit tests for the UDP Broadcaster module.

Tests:
    - Notification payload structure (JSON format)
    - Broadcast retry logic
    - Message content correctness
    - Socket setup

These tests mock the socket to avoid actual network calls.
"""

import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'udp_broadcaster'))

from udp_broadcaster import UDPBroadcaster


@pytest.fixture
def broadcaster():
    """Create a UDP broadcaster instance."""
    return UDPBroadcaster(broadcast_port=9999)


class TestBroadcasterInit:
    """Tests for broadcaster initialisation."""

    def test_default_port(self):
        """Should initialise with specified port."""
        b = UDPBroadcaster(broadcast_port=9999)
        assert b.broadcast_port == 9999

    def test_broadcast_address(self):
        """Should use correct broadcast address."""
        b = UDPBroadcaster(broadcast_port=9999)
        assert b.broadcast_address == '192.168.4.255'


class TestBroadcastMessage:
    """Tests for broadcast message content."""

    @patch.object(UDPBroadcaster, 'setup', return_value=True)
    def test_broadcast_sends_json(self, mock_setup, broadcaster):
        """Broadcast should send valid JSON."""
        broadcaster.sock = MagicMock()
        broadcaster.broadcast_cry_alert("Hungry", 0.92, 0.85, 22.5, 48.0)

        # Get the data that was sent
        call_args = broadcaster.sock.sendto.call_args
        sent_data = call_args[0][0].decode('utf-8')
        parsed = json.loads(sent_data)

        assert parsed["cry_type"] == "Hungry"

    @patch.object(UDPBroadcaster, 'setup', return_value=True)
    def test_broadcast_includes_all_fields(self, mock_setup, broadcaster):
        """Broadcast message should include all required fields."""
        broadcaster.sock = MagicMock()
        broadcaster.broadcast_cry_alert("Pain", 0.88, 0.82, 23.1, 44.8)

        call_args = broadcaster.sock.sendto.call_args
        sent_data = call_args[0][0].decode('utf-8')
        parsed = json.loads(sent_data)

        assert "cry_type" in parsed
        assert "detection_confidence" in parsed
        assert "classification_confidence" in parsed
        assert "temperature" in parsed
        assert "humidity" in parsed
        assert "timestamp" in parsed

    @patch.object(UDPBroadcaster, 'setup', return_value=True)
    def test_broadcast_confidence_values(self, mock_setup, broadcaster):
        """Broadcast should include correct confidence values."""
        broadcaster.sock = MagicMock()
        broadcaster.broadcast_cry_alert("Hungry", 0.92, 0.85, 22.5, 48.0)

        call_args = broadcaster.sock.sendto.call_args
        sent_data = call_args[0][0].decode('utf-8')
        parsed = json.loads(sent_data)

        assert parsed["detection_confidence"] == 0.92
        assert parsed["classification_confidence"] == 0.85

    @patch.object(UDPBroadcaster, 'setup', return_value=True)
    def test_broadcast_sensor_data(self, mock_setup, broadcaster):
        """Broadcast should include temperature and humidity."""
        broadcaster.sock = MagicMock()
        broadcaster.broadcast_cry_alert("Normal", 0.87, 0.65, 22.0, 50.0)

        call_args = broadcaster.sock.sendto.call_args
        sent_data = call_args[0][0].decode('utf-8')
        parsed = json.loads(sent_data)

        assert parsed["temperature"] == 22.0
        assert parsed["humidity"] == 50.0


class TestBroadcastRetry:
    """Tests for broadcast retry logic."""

    @patch.object(UDPBroadcaster, 'broadcast_cry_alert', return_value=True)
    def test_retry_succeeds_on_first_attempt(self, mock_broadcast, broadcaster):
        """Should return True if first attempt succeeds."""
        result = broadcaster.broadcast_with_retry("Hungry", 0.92, 0.85, 22.5, 48.0, max_retries=3)
        assert result is True
        assert mock_broadcast.call_count == 1

    @patch.object(UDPBroadcaster, 'broadcast_cry_alert', side_effect=[False, False, True])
    def test_retry_succeeds_on_third_attempt(self, mock_broadcast, broadcaster):
        """Should retry and succeed on third attempt."""
        result = broadcaster.broadcast_with_retry("Hungry", 0.92, 0.85, 22.5, 48.0, max_retries=3)
        assert result is True
        assert mock_broadcast.call_count == 3

    @patch.object(UDPBroadcaster, 'broadcast_cry_alert', return_value=False)
    def test_retry_fails_after_max_attempts(self, mock_broadcast, broadcaster):
        """Should return False after all retries fail."""
        result = broadcaster.broadcast_with_retry("Hungry", 0.92, 0.85, 22.5, 48.0, max_retries=3)
        assert result is False
        assert mock_broadcast.call_count == 3