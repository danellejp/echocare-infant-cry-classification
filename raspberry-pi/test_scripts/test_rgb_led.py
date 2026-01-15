import time
import RPi.GPIO as GPIO

CLK_PIN = 17  # Pin 11 (White wire)
DATA_PIN = 18  # Pin 12 (Yellow wire)

GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.OUT)

def send_byte(byte):
    for i in range(8):
        GPIO.output(DATA_PIN, (byte & 0x80) != 0)
        GPIO.output(CLK_PIN, GPIO.LOW)
        time.sleep(0.00001)
        GPIO.output(CLK_PIN, GPIO.HIGH)
        time.sleep(0.00001)
        byte <<= 1

def set_color(red, green, blue):
    # Start frame
    for _ in range(4):
        send_byte(0x00)
    
    # Color prefix
    prefix = 0xC0
    if (blue & 0xC0) == 0xC0: prefix |= 0x20
    if (blue & 0x30) == 0x30: prefix |= 0x10
    if (green & 0xC0) == 0xC0: prefix |= 0x08
    if (green & 0x30) == 0x30: prefix |= 0x04
    if (red & 0xC0) == 0xC0: prefix |= 0x02
    if (red & 0x30) == 0x30: prefix |= 0x01
    
    send_byte(prefix)
    send_byte(blue)
    send_byte(green)
    send_byte(red)
    
    # End frame
    for _ in range(4):
        send_byte(0x00)

print("Testing RGB LED...")
print("Red → Green → Blue → Off")

try:
    set_color(255, 0, 0)  # Red
    print("Red")
    time.sleep(2)
    
    set_color(0, 255, 0)  # Green
    print("Green")
    time.sleep(2)
    
    set_color(0, 0, 255)  # Blue
    print("Blue")
    time.sleep(2)
    
    set_color(0, 0, 0)  # Off
    print("Off")
    
finally:
    GPIO.cleanup()
    print("Test complete")