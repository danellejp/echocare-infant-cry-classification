"""
Pretty table viewer for cry events database
"""

from database import CryDatabase

def print_table(events):
    """Print events as a formatted table"""
    if not events:
        print("No events to display")
        return
    
    # Header
    print("\n" + "="*120)
    print(f"{'ID':<5} {'Timestamp':<20} {'Type':<12} {'Det Conf':<10} {'Cls Conf':<10} {'Temp':<8} {'Humidity':<10}")
    print("="*120)
    
    # Rows - events are now tuples: (id, timestamp, cry_type, det_conf, class_conf, temp, humidity)
    for event in events:
        event_id = event[0]
        timestamp = event[1]
        cry_type = event[2]
        detection_conf = event[3]
        classification_conf = event[4]
        temp = event[5]
        humidity = event[6]
        
        # Format temperature and humidity
        temp_str = f"{temp:.1f}°C" if temp is not None and temp >= 0 else "N/A"
        hum_str = f"{humidity:.1f}%" if humidity is not None and humidity >= 0 else "N/A"
        
        print(f"{event_id:<5} "
              f"{timestamp:<20} "
              f"{cry_type:<12} "
              f"{detection_conf:<10.2%} "
              f"{classification_conf:<10.2%} "
              f"{temp_str:<8} "
              f"{hum_str:<10}")
    
    print("="*120 + "\n")

# Main
print("="*120)
print("EchoCare Database - Table View")
print("="*120)

db = CryDatabase()

# Get total
total = db.get_total_events()
print(f"\nTotal events in database: {total}")

if total > 0:
    # Show all events (or limit to recent)
    print(f"\nAll cry events:")
    all_events = db.get_recent_events(limit=100)  # Adjust limit as needed
    print_table(all_events)
    
    # Quick stats
    stats = db.get_statistics(hours=24)
    print("Last 24 Hours Summary:")
    print(f"Total: {stats['total_cries']} cries")
    by_type = stats.get('by_type', {})
    print(f"Hungry: {by_type.get('Hungry', 0)}")
    print(f"Pain: {by_type.get('Pain', 0)}")
    print(f"Normal: {by_type.get('Normal', 0)}")
else:
    print("\nNo events in database yet")
    print("Run cry_detection_v4.py to start logging events")

print("\n" + "="*120 + "\n")

db.close()