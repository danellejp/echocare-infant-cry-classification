"""
EchoCare LED Controller
Handles RGB LED visual indicators
"""

import time
import RPi.GPIO as GPIO
from config import clk_pin, data_pin, led_colours

class LEDController:
    """RGB LED controller for cry type indicators"""
    
    def __init__(self):
        """Initialize GPIO for LED"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(clk_pin, GPIO.OUT)
        GPIO.setup(data_pin, GPIO.OUT)
        GPIO.setwarnings(False)
    
    def send_byte(self, byte):
        """Send a byte to LED via P9813 protocol"""
        for i in range(8):
            GPIO.output(data_pin, (byte & 0x80) != 0)
            GPIO.output(clk_pin, GPIO.LOW)
            time.sleep(0.00001)
            GPIO.output(clk_pin, GPIO.HIGH)
            time.sleep(0.00001)
            byte <<= 1

    def set_color(self, red, green, blue):
        """Set RGB LED color"""
        # Start frame
        for _ in range(4):
            self.send_byte(0x00)
        
        # Calculate prefix
        prefix = 0xC0
        if (blue & 0xC0) == 0xC0: prefix |= 0x20
        if (blue & 0x30) == 0x30: prefix |= 0x10
        if (green & 0xC0) == 0xC0: prefix |= 0x08
        if (green & 0x30) == 0x30: prefix |= 0x04
        if (red & 0xC0) == 0xC0: prefix |= 0x02
        if (red & 0x30) == 0x30: prefix |= 0x01
        
        # Send color
        self.send_byte(prefix)
        self.send_byte(blue)
        self.send_byte(green)
        self.send_byte(red)
        
        # End frame
        for _ in range(4):
            self.send_byte(0x00)
    
    def flash(self, cry_type):
        """Flash LED based on cry type"""
        color = led_colours.get(cry_type, (0, 0, 255))
        flashes = 5 if cry_type in ["Hungry", "Pain"] else 3
        
        for _ in range(flashes):
            self.set_color(*color)
            time.sleep(0.2)
            self.set_color(0, 0, 0)
            time.sleep(0.2)
    
    def off(self):
        """Turn LED off"""
        self.set_color(0, 0, 0)
    
    def test(self):
        """Test LED with RGB sequence"""
        self.set_color(255, 0, 0)  # Red
        time.sleep(0.5)
        self.set_color(0, 255, 0)  # Green
        time.sleep(0.5)
        self.set_color(0, 0, 255)  # Blue
        time.sleep(0.5)
        self.off()
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.off()
        GPIO.cleanup()
