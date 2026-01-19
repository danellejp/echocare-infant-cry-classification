"""
EchoCare - UDP Broadcast Module
Sends real-time cry notifications to Android devices on local network
"""

import socket
import json
import time
from datetime import datetime

class UDPBroadcaster:
    """Handles UDP broadcast notifications for cry detection"""
    
    def __init__(self, broadcast_port=5005):
        """
        Initialize UDP broadcaster
        
        Args:
            broadcast_port: Port to broadcast on (default: 5005)
        """
        self.broadcast_port = broadcast_port
        self.broadcast_address = '<broadcast>'  # Special address for broadcasting
        self.sock = None
        
        print(f"UDP Broadcaster initialized (Port: {broadcast_port})")
    
    def setup(self):
        """Setup UDP socket for broadcasting"""
        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Enable broadcasting
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Set socket timeout (1 second)
            self.sock.settimeout(1.0)
            
            print("UDP socket configured for broadcasting")
            return True
            
        except Exception as e:
            print(f"Failed to setup UDP socket: {e}")
            return False
    
    def broadcast_cry_alert(self, cry_type, detection_confidence, 
                           classification_confidence, temperature=None, 
                           humidity=None):
        """
        Broadcast a cry detection alert to all devices on network
        
        Args:
            cry_type: Type of cry (Hungry, Pain, Normal)
            detection_confidence: Detection model confidence (0-1)
            classification_confidence: Classification model confidence (0-1)
            temperature: Temperature reading (optional)
            humidity: Humidity reading (optional)
        
        Returns:
            bool: True if broadcast successful, False otherwise
        """
        try:
            # Create notification payload
            payload = {
                "event_type": "cry_detected",
                "timestamp": datetime.now().isoformat(),
                "cry_type": cry_type,
                "detection_confidence": round(detection_confidence, 4),
                "classification_confidence": round(classification_confidence, 4),
                "temperature": round(temperature, 1) if temperature and temperature >= 0 else None,
                "humidity": round(humidity, 1) if humidity and humidity >= 0 else None
            }
            
            # Convert to JSON
            message = json.dumps(payload)
            
            # Broadcast the message
            self.sock.sendto(
                message.encode('utf-8'),
                (self.broadcast_address, self.broadcast_port)
            )
            
            print(f"Broadcast sent: {cry_type} (Det: {detection_confidence:.2%}, Class: {classification_confidence:.2%})")
            return True
            
        except Exception as e:
            print(f"Broadcast failed: {e}")
            return False
    
    def broadcast_with_retry(self, cry_type, detection_confidence, 
                            classification_confidence, temperature=None, 
                            humidity=None, max_retries=3):
        """
        Broadcast with automatic retry on failure
        
        Args:
            Same as broadcast_cry_alert, plus:
            max_retries: Number of retry attempts (default: 3)
        
        Returns:
            bool: True if any attempt succeeded
        """
        for attempt in range(max_retries):
            try:
                success = self.broadcast_cry_alert(
                    cry_type, 
                    detection_confidence,
                    classification_confidence,
                    temperature,
                    humidity
                )
                
                if success:
                    return True
                
                # Wait before retry
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries}...")
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
        
        print(f"All {max_retries} broadcast attempts failed")
        return False
    
    def test_broadcast(self):
        """Send a test notification"""
        print("\nSending test broadcast...")
        return self.broadcast_cry_alert(
            cry_type="Test",
            detection_confidence=0.99,
            classification_confidence=0.95,
            temperature=22.5,
            humidity=45.0
        )
    
    def close(self):
        """Close UDP socket"""
        if self.sock:
            self.sock.close()
            print("UDP broadcaster closed")


# ============================================================================
# Test Functions
# ============================================================================

def test_broadcaster():
    """Test UDP broadcasting functionality"""
    print("="*60)
    print("  UDP Broadcaster Test")
    print("="*60)
    
    # Create broadcaster
    broadcaster = UDPBroadcaster(broadcast_port=5005)
    
    # Setup socket
    if not broadcaster.setup():
        print("Failed to setup broadcaster")
        return
    
    # Test 1: Simple broadcast
    print("\nTest 1: Simple broadcast")
    broadcaster.test_broadcast()
    time.sleep(1)
    
    # Test 2: Different cry types
    print("\nTest 2: Different cry types")
    
    print("Broadcasting Hungry cry...")
    broadcaster.broadcast_cry_alert("Hungry", 0.92, 0.85, 22.3, 48.5)
    time.sleep(1)
    
    print("Broadcasting Pain cry...")
    broadcaster.broadcast_cry_alert("Pain", 0.88, 0.82, 23.1, 44.8)
    time.sleep(1)
    
    print("Broadcasting Normal cry...")
    broadcaster.broadcast_cry_alert("Normal", 0.87, 0.65, 22.8, 45.0)
    time.sleep(1)
    
    # Test 3: Broadcast with retry
    print("\nTest 3: Broadcast with retry")
    broadcaster.broadcast_with_retry("Test", 0.95, 0.90, 22.5, 45.0, max_retries=3)
    
    print("\nAll tests complete")
    
    # Cleanup
    broadcaster.close()


if __name__ == "__main__":
    test_broadcaster()