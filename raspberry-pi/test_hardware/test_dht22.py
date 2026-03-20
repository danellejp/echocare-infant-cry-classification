import time
import board
import adafruit_dht

dht = adafruit_dht.DHT22(board.D4)

try:
	temperature = dht.temperature
	humidity = dht.humidity
	print(f"Temperature: {temperature:.1f} degrees celcius")
	print(f"Humidity: {humidity:.1f}%")

except Exception as e:
	print(f"Unexpected error: {e}")

finally:
	dht.exit()
