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
    
    # Rows
    for event in events:
        temp_str = f"{event['temperature']:.1f}°C" if event['temperature'] else "N/A"
        hum_str = f"{event['humidity']:.1f}%" if event['humidity'] else "N/A"
        
        print(f"{event['id']:<5} "
              f"{event['timestamp']:<20} "
              f"{event['cry_type']:<12} "
              f"{event['detection_confidence']:<10.2%} "
              f"{event['classification_confidence']:<10.2%} "
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
    print(f"Hungry: {stats['hungry_count']}")
    print(f"Discomfort: {stats['discomfort_count']}")
    print(f"Normal: {stats['normal_count']}")
else:
    print("\nNo events in database yet")
    print("Run cry_detection_v4.py to start logging events")

print("\n" + "="*120 + "\n")

db.close()