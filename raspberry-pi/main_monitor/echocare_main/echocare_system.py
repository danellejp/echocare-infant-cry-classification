"""
EchoCare - Integrated Cry Monitoring System
Combines all components into a cohesive real-time monitoring system

Components:
- Audio capture and preprocessing
- Two-stage cry detection and classification
- Database logging
- FastAPI backend server
- UDP real-time notifications
- LED visual indicators
- Temperature/humidity monitoring
"""

# Necessary imports
import time
import signal
import sys
from datetime import datetime
import logging

# Import EchoCare modules
from config import *
from database import CryDatabase
from led_controller import LEDController
from audio_preprocess import AudioProcessor
from model_inference import CryDetector
from dht22_reader import get_environment_data
from udp_broadcaster import UDPBroadcaster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/danellepi/echocare/logs/echocare_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('EchoCare')

# EchoCare System Class
class EchoCareSystem:
    """Main EchoCare monitoring system"""
    
    def __init__(self):
        """Initialize all system components"""
        logger.info("EchoCare - Infant Cry Monitoring System")
        logger.info("Initializing...")
        
        # Component references
        self.db = None
        self.led = None
        self.audio = None
        self.detector = None
        self.broadcaster = None
        
        # System state
        self.running = False
        self.iteration_count = 0
        
        # Statistics
        self.stats = {
            'total_iterations': 0,
            'cries_detected': 0,
            'hungry_count': 0,
            'pain_count': 0,
            'normal_count': 0,
            'start_time': None,
            'last_cry_time': None
        }
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Database
            logger.info("Initializing database...")
            self.db = CryDatabase(database_path)
            logger.info("Database initialized")
            
            # LED Controller
            logger.info("Initializing LED controller...")
            self.led = LEDController()
            logger.info("LED controller initialized")
            
            # Audio Processor
            logger.info("Initializing audio processor...")
            self.audio = AudioProcessor()
            logger.info("Audio processor initialized")
            
            # Model Inference
            logger.info("Loading AI models...")
            self.detector = CryDetector()
            logger.info("Models loaded")
            
            # UDP Broadcaster
            logger.info("Setting up UDP broadcaster...")
            self.broadcaster = UDPBroadcaster(broadcast_port=5005)
            self.broadcaster.setup()
            logger.info("UDP broadcaster ready")
            
            # Test LED
            logger.info("\nTesting LED...")
            self.led.test()
            logger.info("LED test complete")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            raise
    
    def process_audio_chunk(self):
        """
        Process one audio chunk through the complete pipeline:
        Audio → Detection → Classification → Database → UDP → LED
        
        Returns:
            bool: True if cry detected, False otherwise
        """
        try:
            # Capture audio
            raw_audio = self.audio.capture()
            
            # Preprocess for detection
            preprocessed_detection = self.audio.preprocess(
                raw_audio, 
                cry_detection_mean, 
                cry_detection_std
            )
            
            # Stage 1: Detection
            detection_confidence = self.detector.detect(preprocessed_detection)
            is_cry = detection_confidence >= detection_threshold
            
            if is_cry:
                logger.info(f"CRY DETECTED! (Confidence: {detection_confidence:.2%})")
                
                # Preprocess for classification
                preprocessed_classification = self.audio.preprocess(
                    raw_audio,
                    cry_classification_mean,
                    cry_classification_std
                )
                
                # Stage 2: Classification
                classification_score = self.detector.classify(preprocessed_classification)
                cry_type, classification_confidence = self.detector.process_cry(classification_score)
                
                logger.info(f"Classification: {cry_type} (Confidence: {classification_confidence:.2%})")
                
                # Read environment sensors
                temperature, humidity = get_environment_data(max_retries=3)
                
                if temperature == -1.0:
                    logger.warning("Environment sensor unavailable")
                else:
                    logger.info(f"Environment: {temperature:.1f}°C, {humidity:.1f}%")
                
                # Update statistics
                self.stats['cries_detected'] += 1
                self.stats['last_cry_time'] = datetime.now()
                
                if cry_type == "Hungry":
                    self.stats['hungry_count'] += 1
                elif cry_type == "Pain":
                    self.stats['pain_count'] += 1
                else:
                    self.stats['normal_count'] += 1
                
                # Log to database
                event_id = self.db.insert_cry_event(
                    cry_type=cry_type,
                    detection_conf=detection_confidence,
                    class_conf=classification_confidence,
                    temperature=temperature,
                    humidity=humidity
                )
                logger.info(f"Logged to database (Event ID: {event_id})")
                
                # Broadcast UDP notification
                broadcast_success = self.broadcaster.broadcast_with_retry(
                    cry_type=cry_type,
                    detection_confidence=detection_confidence,
                    classification_confidence=classification_confidence,
                    temperature=temperature,
                    humidity=humidity,
                    max_retries=3
                )
                
                if broadcast_success:
                    logger.info("UDP notification sent")
                else:
                    logger.warning("UDP notification failed")
                
                # Flash LED
                self.led.flash(cry_type)
                
                logger.info(f"LED: {cry_type} color")
                
                return True
            
            else:
                # No cry detected
                self.led.off()
                return False
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return False
    
    def print_status(self):
        """Print current system status"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds() / 60
        
        logger.info("SYSTEM STATUS")
        logger.info(f"Uptime: {uptime:.1f} minutes")
        logger.info(f"Iterations: {self.stats['total_iterations']}")
        logger.info(f"Total cries detected: {self.stats['cries_detected']}")
        logger.info(f"Hungry: {self.stats['hungry_count']}")
        logger.info(f"Pain: {self.stats['pain_count']}")
        logger.info(f"Normal: {self.stats['normal_count']}")
        
        if self.stats['last_cry_time']:
            time_since_last = (datetime.now() - self.stats['last_cry_time']).total_seconds()
            logger.info(f"Last cry: {time_since_last:.0f} seconds ago")
        
        # Database stats
        total_events = self.db.get_total_events()
        logger.info(f"Database: {total_events} total events")
    
    def run(self):
        """Main monitoring loop"""
        logger.info("\nStarting EchoCare monitoring system...")
        logger.info("Press Ctrl+C to stop\n")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        last_status_time = time.time()
        status_interval = 300  # Print status every 5 minutes
        
        try:
            while self.running:
                self.iteration_count += 1
                self.stats['total_iterations'] = self.iteration_count
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Process audio chunk
                cry_detected = self.process_audio_chunk()
                
                if not cry_detected:
                    # Silent - print minimal log
                    if self.iteration_count % 10 == 0:  # Log every 10th iteration
                        logger.debug(f"[{timestamp}] Monitoring... (Iteration {self.iteration_count})")
                
                # Print status update every 5 minutes
                current_time = time.time()
                if current_time - last_status_time >= status_interval:
                    self.print_status()
                    last_status_time = current_time
                
                # Small delay between iterations
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            logger.info("\n\nMonitoring stopped by user (Ctrl+C)")
            self.print_status()
        
        except Exception as e:
            logger.error(f"\nSystem error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of all components"""
        logger.info("\nShutting down EchoCare system...")
        
        try:
            if self.led:
                self.led.cleanup()
                logger.info("LED cleaned up")
            
            if self.audio:
                self.audio.terminate()
                logger.info("Audio processor closed")
            
            if self.db:
                self.db.close()
                logger.info("Database connection closed")
            
            if self.broadcaster:
                self.broadcaster.close()
                logger.info("UDP broadcaster closed")
            
            logger.info("\nShutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# signal handlers
system = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    if system:
        system.running = False

# main entry point
def main():
    """Main entry point"""
    global system
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run system
    system = EchoCareSystem()
    system.run()


if __name__ == "__main__":
    main()