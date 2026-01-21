"""
EchoCare - System Health Monitor
Checks CPU, memory, disk usage during operation
"""

import psutil
import time
from datetime import datetime

def monitor_system_health(duration_minutes=20, interval_seconds=30):
    """
    Monitor system resources while EchoCare is running
    
    Args:
        duration_minutes: How long to monitor
        interval_seconds: How often to check
    """

    print("  EchoCare System Health Monitor")
    print(f"Monitoring for {duration_minutes} minutes")
    print(f"Checking every {interval_seconds} seconds")
    
    iterations = (duration_minutes * 60) // interval_seconds
    
    for i in range(iterations):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Temperature (if available)
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                cpu_temp = temps['cpu_thermal'][0].current
            else:
                cpu_temp = None
        except:
            cpu_temp = None
        
        # Print status
        print(f"[{timestamp}] CPU: {cpu_percent:5.1f}% | "
              f"Memory: {memory_percent:5.1f}% ({memory_used_mb:.0f}/{memory_total_mb:.0f} MB) | "
              f"Disk: {disk_percent:5.1f}%", end="")
        
        if cpu_temp:
            print(f" | Temp: {cpu_temp:.1f}°C", end="")
        
        print()
        
        # Warnings
        if cpu_percent > 80:
            print("WARNING: High CPU usage")
        if memory_percent > 80:
            print("WARNING: High memory usage")
        if cpu_temp and cpu_temp > 70:
            print("WARNING: High CPU temperature")
        
        time.sleep(interval_seconds)
    
    print("Health monitoring complete")


if __name__ == "__main__":
    # Run for 20 minutes by default
    monitor_system_health(duration_minutes=20, interval_seconds=30)