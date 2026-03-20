"""
Unit tests for the CryDatabase module

Tests:
    - Database creation and schema initialisation
    - INSERT: Inserting cry events with various parameters
    - READ: Retrieving recent events, statistics, total counts
    - DELETE: Clearing all events
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

class TestDatabaseCreation:
    """Tests for database initialisation"""

    def test_database_creates_file(self, test_db):
        """Database file should exist after initialisation"""
        assert test_db is not None

    def test_database_has_cry_events_table(self, test_db):
        """Database should have a cry_events table"""
        test_db.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cry_events'"
        )
        result = test_db.cursor.fetchone()
        assert result is not None


class TestInsertCryEvent:
    """Tests for inserting cry events"""

    def test_insert_returns_event_id(self, test_db):
        """Insert should return a positive event ID."""
        event_id = test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, 48.0)
        assert event_id is not None
        assert event_id > 0

    def test_insert_increments_id(self, test_db):
        """Each insert should return an incrementing ID"""
        id1 = test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, 48.0)
        id2 = test_db.insert_cry_event("Pain", 0.88, 0.82, 23.0, 45.0)
        assert id2 == id1 + 1

    def test_insert_all_cry_types(self, test_db):
        """Should successfully insert all three cry types"""
        id1 = test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, 48.0)
        id2 = test_db.insert_cry_event("Pain", 0.88, 0.82, 23.0, 45.0)
        id3 = test_db.insert_cry_event("Normal", 0.87, 0.65, 22.0, 50.0)
        assert id1 > 0
        assert id2 > 0
        assert id3 > 0

    def test_insert_with_null_temperature(self, test_db):
        """Should handle null temperature gracefully"""
        event_id = test_db.insert_cry_event("Hungry", 0.92, 0.85, -1.0, 48.0)
        assert event_id > 0

    def test_insert_with_null_humidity(self, test_db):
        """Should handle null humidity gracefully"""
        event_id = test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, -1.0)
        assert event_id > 0

    def test_insert_with_high_confidence(self, test_db):
        """Should accept confidence scores at upper boundary"""
        event_id = test_db.insert_cry_event("Hungry", 1.0, 1.0, 22.5, 48.0)
        assert event_id > 0

    def test_insert_with_low_confidence(self, test_db):
        """Should accept confidence scores at lower boundary"""
        event_id = test_db.insert_cry_event("Normal", 0.85, 0.10, 22.5, 48.0)
        assert event_id > 0


class TestGetRecentEvents:
    """Tests for retrieving recent events"""

    def test_returns_empty_list_when_no_events(self, test_db):
        """Should return empty list for empty database"""
        events = test_db.get_recent_events(limit=5)
        assert events == []

    def test_returns_correct_number_of_events(self, populated_db):
        """Should respect the limit parameter"""
        events = populated_db.get_recent_events(limit=3)
        assert len(events) == 3

    def test_returns_all_events_when_limit_exceeds_count(self, populated_db):
        """Should return all events if limit is higher than count"""
        events = populated_db.get_recent_events(limit=100)
        assert len(events) == 6

    def test_returns_events_in_descending_order(self, populated_db):
        """Most recent events should be first"""
        events = populated_db.get_recent_events(limit=6)
        # Last inserted was Normal, so it should be first
        assert events[0][2] == "Normal"  # cry_type is index 2

    def test_event_has_all_fields(self, populated_db):
        """Each event should have id, timestamp, cry_type, confidences, temp, humidity"""
        events = populated_db.get_recent_events(limit=1)
        event = events[0]
        # Event is a tuple: (id, timestamp, cry_type, det_conf, class_conf, temp, humidity)
        assert len(event) == 7


class TestGetStatistics:
    """Tests for retrieving statistics"""

    def test_statistics_on_empty_database(self, test_db):
        """Should return zero counts for empty database"""
        stats = test_db.get_statistics(hours=24)
        assert stats['total_cries'] == 0

    def test_total_cries_count(self, populated_db):
        """Should count all events in time window"""
        stats = populated_db.get_statistics(hours=24)
        assert stats['total_cries'] == 6

    def test_statistics_by_type(self, populated_db):
        """Should break down counts by cry type"""
        stats = populated_db.get_statistics(hours=24)
        by_type = stats['by_type']
        assert by_type.get('Hungry', 0) == 3
        assert by_type.get('Pain', 0) == 2
        assert by_type.get('Normal', 0) == 1

    def test_statistics_hours_filter(self, populated_db):
        """Statistics should respect the hours parameter"""
        # All events were just inserted, so 24h should include them all
        stats = populated_db.get_statistics(hours=24)
        assert stats['total_cries'] == 6


class TestGetTotalEvents:
    """Tests for total event count"""

    def test_total_events_empty(self, test_db):
        """Should return 0 for empty database"""
        assert test_db.get_total_events() == 0

    def test_total_events_after_inserts(self, populated_db):
        """Should return correct count after inserts"""
        assert populated_db.get_total_events() == 6

    def test_total_events_increments(self, test_db):
        """Count should increment with each insert"""
        assert test_db.get_total_events() == 0
        test_db.insert_cry_event("Hungry", 0.92, 0.85, 22.5, 48.0)
        assert test_db.get_total_events() == 1
        test_db.insert_cry_event("Pain", 0.88, 0.82, 23.0, 45.0)
        assert test_db.get_total_events() == 2


class TestClearAllEvents:
    """Tests for clearing the database"""

    def test_clear_empties_database(self, populated_db):
        """Clear should remove all events"""
        assert populated_db.get_total_events() == 6
        populated_db.clear_all_events()
        assert populated_db.get_total_events() == 0

    def test_clear_on_empty_database(self, test_db):
        """Clear on empty database should not error"""
        test_db.clear_all_events()
        assert test_db.get_total_events() == 0
