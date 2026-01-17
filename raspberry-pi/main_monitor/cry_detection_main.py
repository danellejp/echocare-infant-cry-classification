"""
EchoCare - Main Monitoring Script
Modular, clean, maintainable
"""

# Import our modules
from config import *
from database import CryDatabase
from led_controller import LEDController
from audio_preprocess import AudioProcessor
from model_inference import CryDetector
import time
from datetime import datetime
from dht22_reader import get_environment_data

print("EchoCare - Cry Detection System")

# Initialize components
print("\nInitializing components...")
db = CryDatabase(database_path)
led = LEDController()
audio = AudioProcessor()
detector = CryDetector()
print("All components ready")

# Statistics
stats = {
    "total_iterations": 0,
    "cries_detected": 0,
    "hungry_count": 0,
    "pain_count": 0,
    "normal_count": 0
}

# Test LED
print("\nTesting LED...")
led.test()
print("LED test complete")

print("\nStarting monitoring...")
print("Press Ctrl+C to stop\n")

try:
    iteration = 0
    
    while True:
        iteration += 1
        stats['total_iterations'] = iteration
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] Iteration {iteration}")
        
        # Capture audio
        raw_audio = audio.capture()
        
        # Preprocess for detection
        preprocessed_detection = audio.preprocess(
            raw_audio, 
            cry_detection_mean, 
            cry_detection_std
        )
        
        # Run detection
        detection_confidence = detector.detect(preprocessed_detection)
        is_cry = detection_confidence >= detection_threshold
        
        if is_cry:
            stats['cries_detected'] += 1
            
            # Preprocess for classification
            preprocessed_classification = audio.preprocess(
                raw_audio,
                cry_classification_mean,
                cry_classification_std
            )
            
            # Classify cry
            classification_score = detector.classify(preprocessed_classification)
            cry_type, classification_confidence = detector.process_cry(classification_score)
            
            # Update stats
            if cry_type == "Hungry":
                stats['hungry_count'] += 1
            elif cry_type == "Pain":
                stats['pain_count'] += 1
            else:
                stats['normal_count'] += 1
            
            # Display result
            print(f"CRY: {cry_type}")
            print(f"Detection: {detection_confidence:.2%}")
            print(f"Classification: {classification_confidence:.2%}")
            
            temperature, humidity = get_environment_data(max_retries=3)
            
            if temperature == -1.0:
                print("Environment sensor unavailable")
            else:
                print(f"Temp: {temperature:.1f}°C, Humidity: {humidity:.1f}%")

            # Log to database
            event_id = db.insert_cry_event(
                cry_type=cry_type,
                detection_conf=detection_confidence,
                class_conf=classification_confidence,
                temperature=temperature,
                humidity=humidity
            )
            print(f"Logged as event #{event_id}")
            
            # Flash LED
            led.flash(cry_type)

        else:
            print(f"No cry ({detection_confidence:.2%})")
            led.off()
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\nStopped by user")
    
    # Show stats
    print("\nSession Statistics:")
    print(f"Iterations: {stats['total_iterations']}")
    print(f"Cries detected: {stats['cries_detected']}")
    print(f"Hungry: {stats['hungry_count']}")
    print(f"Pain: {stats['pain_count']}")
    print(f"Normal: {stats['normal_count']}")
    
    # Database stats for last 24 hours
    db_stats = db.get_statistics(hours=24)
    print(f"\nDatabase: {db.get_total_events()} total events")

finally:
    # Cleanup
    led.cleanup()
    audio.terminate()
    db.close()
    print("\nCleanup complete\n")