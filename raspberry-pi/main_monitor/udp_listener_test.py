"""
EchoCare - UDP Listener Test
Used to verify broadcasts are being received
"""

import socket
import json

def listen_for_broadcasts(port=5005):
    """Listen for UDP broadcasts on specified port"""
    
    print(f"UDP Listener - Waiting for broadcasts on port {port}")
    print("Press Ctrl+C to stop")
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to all interfaces on the specified port
    sock.bind(('', port))
    
    print(f"Listening on port {port}...\n")
    
    try:
        while True:
            # Receive data
            data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
            
            # Decode and parse JSON
            message = data.decode('utf-8')
            notification = json.loads(message)
            
            # Display notification
            print(f"NOTIFICATION RECEIVED from {addr[0]}")
            print(f"Event Type: {notification['event_type']}")
            print(f"Timestamp: {notification['timestamp']}")
            print(f"Cry Type: {notification['cry_type']}")
            print(f"Detection Confidence: {notification['detection_confidence']:.2%}")
            print(f"Classification Confidence: {notification['classification_confidence']:.2%}")
            
            if notification['temperature']:
                print(f"Temperature: {notification['temperature']}°C")
            if notification['humidity']:
                print(f"Humidity: {notification['humidity']}%")
            
    except KeyboardInterrupt:
        print("\n\nListener stopped")
    finally:
        sock.close()


if __name__ == "__main__":
    listen_for_broadcasts(port=5005)