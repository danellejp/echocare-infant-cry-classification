"""
EchoCare Database Module
Handles all SQLite database operations for cry event logging
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class CryDatabase:
    """SQLite database manager for cry events"""
    
    def __init__(self, db_path="/home/danellepi/echocare/echocare.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect and initialize
        self.connect()
        self.initialize_schema()
    
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
    
    def initialize_schema(self):
        """Create tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cry_type TEXT NOT NULL,
                detection_confidence REAL NOT NULL,
                classification_confidence REAL NOT NULL,
                temperature REAL,
                humidity REAL
            )
        ''')
        
        # Create index on timestamp for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON cry_events(timestamp)
        ''')
        
        self.conn.commit()
        print("Database schema initialised")
    
    def insert_cry_event(self, cry_type, detection_conf, class_conf, 
                        temperature=None, humidity=None):
        """
        Insert a new cry event
        
        Args:
            cry_type: Cry classification (Hungry, Pain, Normal)
            detection_conf: Detection model confidence (0-1)
            class_conf: Classification model confidence (0-1)
            temperature: Temperature reading in Celsius (optional)
            humidity: Humidity percentage (optional)
        
        Returns:
            int: ID of inserted row
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute('''
            INSERT INTO cry_events 
            (timestamp, cry_type, detection_confidence, 
             classification_confidence, temperature, humidity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, cry_type, detection_conf, class_conf, 
              temperature, humidity))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_recent_events(self, limit=10):
        """
        Get most recent cry events with proper type casting
        
        Args:
            limit: Number of events to retrieve
        
        Returns:
            list: List of tuples (id, timestamp, cry_type, detection_conf, class_conf, temp, humidity)
        """
        self.cursor.execute('''
            SELECT 
                id,
                timestamp,
                cry_type,
                CAST(detection_confidence AS REAL) as detection_confidence,
                CAST(classification_confidence AS REAL) as classification_confidence,
                CAST(temperature AS REAL) as temperature,
                CAST(humidity AS REAL) as humidity
            FROM cry_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        # Return as list of tuples (not dictionaries) to match API expectations
        return self.cursor.fetchall()
    
    def get_statistics(self, hours=24):
        """
        Get cry statistics for the past N hours with proper type casting
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            dict: Statistics including counts by type
        """
        # Calculate timestamp for N hours ago
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_cries,
                SUM(CASE WHEN cry_type = 'Hungry' THEN 1 ELSE 0 END) as hungry_count,
                SUM(CASE WHEN cry_type = 'Pain' THEN 1 ELSE 0 END) as pain_count,
                SUM(CASE WHEN cry_type = 'Normal' THEN 1 ELSE 0 END) as normal_count,
                AVG(CAST(temperature AS REAL)) as avg_temperature,
                AVG(CAST(humidity AS REAL)) as avg_humidity,
                AVG(CAST(classification_confidence AS REAL)) as avg_confidence
            FROM cry_events
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
        ''', (hours,))
        
        row = self.cursor.fetchone()
        
        # Calculate average temperature (excluding -1 values)
        self.cursor.execute('''
            SELECT AVG(CAST(temperature AS REAL)) as avg_temp
            FROM cry_events
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            AND CAST(temperature AS REAL) >= 0
        ''', (hours,))
        
        temp_row = self.cursor.fetchone()
        avg_temp = round(temp_row['avg_temp'], 1) if temp_row['avg_temp'] else None
        
        # Calculate average humidity (excluding -1 values)
        self.cursor.execute('''
            SELECT AVG(CAST(humidity AS REAL)) as avg_humidity
            FROM cry_events
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            AND CAST(humidity AS REAL) >= 0
        ''', (hours,))
        
        humid_row = self.cursor.fetchone()
        avg_humidity = round(humid_row['avg_humidity'], 1) if humid_row['avg_humidity'] else None
        
        return {
            'total_cries': row['total_cries'] or 0,
            'by_type': {
                'Hungry': row['hungry_count'] or 0,
                'Pain': row['pain_count'] or 0,
                'Normal': row['normal_count'] or 0
            },
            'average_confidence': round(row['avg_confidence'], 4) if row['avg_confidence'] else 0,
            'avg_temperature': avg_temp,
            'avg_humidity': avg_humidity
        }
    
    def get_cry_pattern(self, hours=24):
        """
        Get hourly cry distribution pattern
        
        Args:
            hours: Number of hours to analyze
        
        Returns:
            list: Hourly cry counts
        """
        self.cursor.execute('''
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM cry_events
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            GROUP BY hour
            ORDER BY hour
        ''', (hours,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_total_events(self):
        """Get total number of cry events in database"""
        self.cursor.execute('SELECT COUNT(*) as count FROM cry_events')
        return self.cursor.fetchone()['count']
    
    def clear_all_events(self): # use with caution
        """Delete all cry events"""
        self.cursor.execute('DELETE FROM cry_events')
        self.conn.commit()
        print("All cry events deleted")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================
# Test Functions
# ============================================

def test_database():
    """Test database functionality"""
    print("Database Module Test")
    
    # Create database instance
    db = CryDatabase()
    
    # Test 1: Insert events
    print("\nTest 1: Inserting dummy test events...")
    db.insert_cry_event("Hungry", 0.92, 0.78, 22.5, 45.2)
    db.insert_cry_event("Pain", 0.88, 0.82, 23.1, 44.8)
    db.insert_cry_event("Normal", 0.87, 0.65, 22.8, 45.0)
    print("3 events inserted")
    
    # Test 2: Get recent events
    print("\nTest 2: Retrieving recent events...")
    recent = db.get_recent_events(limit=5)
    for event in recent:
        # event is now a tuple: (id, timestamp, cry_type, det_conf, class_conf, temp, humidity)
        print(f"[{event[1]}] {event[2]} "
              f"(Detection: {event[3]:.2%}, "
              f"Classification: {event[4]:.2%})")
    print("Recent events retrieved")
    
    # Test 3: Get statistics
    print("\nTest 3: Getting statistics...")
    stats = db.get_statistics(hours=24)
    print(f"Total cries: {stats['total_cries']}")
    print(f"By type: {stats['by_type']}")
    print(f"Average confidence: {stats['average_confidence']:.2%}")
    if stats['avg_temperature']:
        print(f"Avg temperature: {stats['avg_temperature']}°C")
        print(f"Avg humidity: {stats['avg_humidity']}%")
    print("Statistics retrieved")
    
    # Test 4: Get total count
    print("\nTest 4: Total events in database...")
    total = db.get_total_events()
    print(f"Total events: {total}")
    print("Total count retrieved")

    # Test 5: Cry pattern
    print("\nTest 5: Hourly cry pattern...")
    pattern = db.get_cry_pattern(hours=24)
    if pattern:
        for item in pattern:
            print(f"Hour {item['hour']}:00 - {item['count']} cries")
    else:
        print("No pattern data (need more events)")
    print("Pattern retrieved")
    
    print("All database tests passed!")

    # Close connection
    db.close()


if __name__ == "__main__":
    test_database()