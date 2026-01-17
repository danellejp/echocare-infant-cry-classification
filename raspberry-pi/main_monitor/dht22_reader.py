# sensor_reader.py
"""
DHT22 Temperature and Humidity Sensor Reader
Provides robust sensor reading with retry logic and validation
"""

import adafruit_dht
import board
import time
from typing import Tuple, Optional

class SensorReader:
    def __init__(self, pin=board.D4, sensor_type="DHT22"):
        """
        Initialize sensor reader
        
        Args:
            pin: GPIO pin for sensor (default: D4)
            sensor_type: Type of sensor (DHT22)
        """
        self.pin = pin
        self.sensor_type = sensor_type
        self.last_good_reading = {"temperature": None, "humidity": None, "timestamp": None}
        
        self.sensor = adafruit_dht.DHT22(pin)
    
    def read(self, max_retries=3, delay=2.0, use_cache=True) -> Tuple[Optional[float], Optional[float]]:
        """
        Read temperature and humidity with retry logic
        
        Args:
            max_retries: Number of retry attempts
            delay: Delay between retries in seconds
            use_cache: If True, return last good reading if current read fails
        
        Returns:
            Tuple of (temperature, humidity) or (None, None)
        """
        for attempt in range(max_retries):
            try:
                temperature = self.sensor.temperature
                humidity = self.sensor.humidity
                
                # Validate readings
                if self._is_valid_reading(temperature, humidity):
                    # Update cache
                    self.last_good_reading = {
                        "temperature": temperature,
                        "humidity": humidity,
                        "timestamp": time.time()
                    }
                    return temperature, humidity
                
            except RuntimeError as e:
                # Common DHT sensor error - sensor not ready
                if attempt < max_retries - 1:
                    time.sleep(delay)
            
            except Exception as e:
                print(f"Unexpected sensor error: {e}")
                break
        
        # All retries failed
        if use_cache and self.last_good_reading["temperature"] is not None:
            # Use cached reading if it's less than 5 minutes old
            age = time.time() - self.last_good_reading["timestamp"]
            if age < 300:  # 5 minutes
                print(f"Using cached reading ({age:.0f}s old)")
                return self.last_good_reading["temperature"], self.last_good_reading["humidity"]
        
        return None, None
    
    def _is_valid_reading(self, temperature, humidity):
        """Validate sensor readings are within reasonable ranges"""
        if temperature is None or humidity is None:
            return False
        
        return -40 <= temperature <= 80 and 0 <= humidity <= 100
    
    def cleanup(self):
        """Cleanup sensor resources"""
        try:
            self.sensor.exit()
        except:
            pass


# Convenience function for quick use
def get_environment_data(max_retries=3) -> Tuple[float, float]:
    """
    Quick function to get temperature and humidity
    Returns (-1.0, -1.0) if sensor fails
    """
    sensor = SensorReader()
    temp, humid = sensor.read(max_retries=max_retries, use_cache=True)
    sensor.cleanup()
    
    if temp is None:
        return -1.0, -1.0
    
    return temp, humid