"""
Advanced AI Exam Monitoring System Configuration
نظام تكوين متطور لمراقبة الامتحانات بالذكاء الاصطناعي
"""

import os
from typing import Dict, List, Tuple

class Config:
    """Configuration class for the Advanced AI Exam Monitoring System"""
    
    # System Configuration
    SYSTEM_NAME = "Advanced AI Exam Monitor"
    VERSION = "2.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Video Configuration
    CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
    FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "1280"))
    FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "720"))
    FPS = int(os.getenv("FPS", "30"))
    
    # AI Model Configuration
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.5"))
    
    # MediaPipe Configuration
    MEDIAPIPE_FACE_DETECTION_CONFIDENCE = float(os.getenv("FACE_DETECTION_CONFIDENCE", "0.5"))
    MEDIAPIPE_FACE_MESH_CONFIDENCE = float(os.getenv("FACE_MESH_CONFIDENCE", "0.5"))
    MEDIAPIPE_POSE_CONFIDENCE = float(os.getenv("POSE_CONFIDENCE", "0.5"))
    MEDIAPIPE_TRACKING_CONFIDENCE = float(os.getenv("TRACKING_CONFIDENCE", "0.5"))
    
    # Face Movement Tracking Configuration
    FACE_MOVEMENT_THRESHOLD = float(os.getenv("FACE_MOVEMENT_THRESHOLD", "3.0"))  # seconds
    FACE_MOVEMENT_SENSITIVITY = int(os.getenv("FACE_MOVEMENT_SENSITIVITY", "50"))  # pixels
    FACE_MOVEMENT_HISTORY_SIZE = int(os.getenv("FACE_MOVEMENT_HISTORY_SIZE", "30"))  # frames
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "1024"))
    AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
    
    # Sound Detection Configuration
    SOUND_AMPLITUDE_THRESHOLDS = {
        'high': int(os.getenv("SOUND_HIGH_AMPLITUDE", "1000")),
        'medium': int(os.getenv("SOUND_MEDIUM_AMPLITUDE", "500")),
        'low': int(os.getenv("SOUND_LOW_AMPLITUDE", "100"))
    }
    
    SOUND_FREQUENCY_THRESHOLDS = {
        'high': int(os.getenv("SOUND_HIGH_FREQUENCY", "1000")),
        'medium': int(os.getenv("SOUND_MEDIUM_FREQUENCY", "500")),
        'low': int(os.getenv("SOUND_LOW_FREQUENCY", "100"))
    }
    
    SOUND_DETECTION_COUNTS = {
        'whispering': int(os.getenv("WHISPERING_COUNT", "5")),
        'talking': int(os.getenv("TALKING_COUNT", "3")),
        'keyboard_typing': int(os.getenv("KEYBOARD_COUNT", "5")),
        'paper_rustling': int(os.getenv("PAPER_COUNT", "8")),
        'phone_vibration': int(os.getenv("PHONE_COUNT", "3"))
    }
    
    # Time Thresholds (seconds)
    TIME_THRESHOLDS = {
        'face_away': float(os.getenv("FACE_AWAY_THRESHOLD", "5.0")),
        'person_absent': float(os.getenv("PERSON_ABSENT_THRESHOLD", "3.0")),
        'talking': float(os.getenv("TALKING_THRESHOLD", "2.0")),
        'face_movement': float(os.getenv("FACE_MOVEMENT_THRESHOLD", "3.0"))
    }
    
    # Score Penalties
    SCORE_PENALTIES = {
        'multiple_people': int(os.getenv("MULTIPLE_PEOPLE_PENALTY", "20")),
        'face_away': int(os.getenv("FACE_AWAY_PENALTY", "10")),
        'forbidden_object': int(os.getenv("FORBIDDEN_OBJECT_PENALTY", "25")),
        'person_absent': int(os.getenv("PERSON_ABSENT_PENALTY", "15")),
        'talking': int(os.getenv("TALKING_PENALTY", "20")),
        'face_movement': int(os.getenv("FACE_MOVEMENT_PENALTY", "15")),
        'suspicious_sounds': int(os.getenv("SUSPICIOUS_SOUNDS_PENALTY", "15"))
    }
    
    # Forbidden Objects
    FORBIDDEN_OBJECTS = [
        'cell phone', 'book', 'laptop', 'tablet', 'headphone', 'earphone',
        'paper', 'notebook', 'calculator', 'watch', 'glasses_case'
    ]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "cheating_log.txt")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10"))  # MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Dashboard Configuration
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "localhost")
    DASHBOARD_TITLE = "Advanced AI Exam Monitor Dashboard"
    
    # Alert Configuration
    MAX_ALERTS_DISPLAY = int(os.getenv("MAX_ALERTS_DISPLAY", "5"))
    ALERT_HISTORY_SIZE = int(os.getenv("ALERT_HISTORY_SIZE", "10"))
    
    # Performance Configuration
    FRAME_PROCESSING_INTERVAL = float(os.getenv("FRAME_PROCESSING_INTERVAL", "0.033"))  # 30 FPS
    AUDIO_PROCESSING_INTERVAL = float(os.getenv("AUDIO_PROCESSING_INTERVAL", "0.1"))  # 10 Hz
    
    # Security Configuration
    ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "False").lower() == "true"
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key-change-in-production")
    
    # Notification Configuration
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False").lower() == "true"
    ENABLE_SMS_NOTIFICATIONS = os.getenv("ENABLE_SMS_NOTIFICATIONS", "False").lower() == "true"
    ENABLE_DESKTOP_NOTIFICATIONS = os.getenv("ENABLE_DESKTOP_NOTIFICATIONS", "True").lower() == "true"
    
    # Database Configuration (if using)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///exam_monitor.db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    
    @classmethod
    def get_face_movement_config(cls) -> Dict:
        """Get face movement tracking configuration"""
        return {
            'threshold': cls.FACE_MOVEMENT_THRESHOLD,
            'sensitivity': cls.FACE_MOVEMENT_SENSITIVITY,
            'history_size': cls.FACE_MOVEMENT_HISTORY_SIZE
        }
    
    @classmethod
    def get_sound_detection_config(cls) -> Dict:
        """Get sound detection configuration"""
        return {
            'amplitude_thresholds': cls.SOUND_AMPLITUDE_THRESHOLDS,
            'frequency_thresholds': cls.SOUND_FREQUENCY_THRESHOLDS,
            'detection_counts': cls.SOUND_DETECTION_COUNTS
        }
    
    @classmethod
    def get_ai_model_config(cls) -> Dict:
        """Get AI model configuration"""
        return {
            'yolo_model_path': cls.YOLO_MODEL_PATH,
            'yolo_confidence': cls.YOLO_CONFIDENCE_THRESHOLD,
            'face_detection_confidence': cls.MEDIAPIPE_FACE_DETECTION_CONFIDENCE,
            'face_mesh_confidence': cls.MEDIAPIPE_FACE_MESH_CONFIDENCE,
            'pose_confidence': cls.MEDIAPIPE_POSE_CONFIDENCE,
            'tracking_confidence': cls.MEDIAPIPE_TRACKING_CONFIDENCE
        }
    
    @classmethod
    def get_time_thresholds(cls) -> Dict:
        """Get time threshold configuration"""
        return cls.TIME_THRESHOLDS.copy()
    
    @classmethod
    def get_score_penalties(cls) -> Dict:
        """Get score penalty configuration"""
        return cls.SCORE_PENALTIES.copy()
    
    @classmethod
    def get_forbidden_objects(cls) -> List[str]:
        """Get list of forbidden objects"""
        return cls.FORBIDDEN_OBJECTS.copy()
    
    @classmethod
    def validate_config(cls) -> Tuple[bool, List[str]]:
        """Validate configuration values"""
        errors = []
        
        # Validate numeric values
        if cls.FRAME_WIDTH <= 0 or cls.FRAME_HEIGHT <= 0:
            errors.append("Frame dimensions must be positive")
            
        if cls.FPS <= 0:
            errors.append("FPS must be positive")
            
        if cls.FACE_MOVEMENT_THRESHOLD <= 0:
            errors.append("Face movement threshold must be positive")
            
        if cls.FACE_MOVEMENT_SENSITIVITY <= 0:
            errors.append("Face movement sensitivity must be positive")
            
        # Validate file paths
        if not os.path.exists(cls.YOLO_MODEL_PATH):
            errors.append(f"YOLO model not found: {cls.YOLO_MODEL_PATH}")
            
        # Validate thresholds
        for threshold_name, threshold_value in cls.TIME_THRESHOLDS.items():
            if threshold_value <= 0:
                errors.append(f"{threshold_name} threshold must be positive")
                
        for penalty_name, penalty_value in cls.SCORE_PENALTIES.items():
            if penalty_value < 0 or penalty_value > 100:
                errors.append(f"{penalty_name} penalty must be between 0 and 100")
                
        return len(errors) == 0, errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print(f"\n{'='*50}")
        print(f"{cls.SYSTEM_NAME} v{cls.VERSION}")
        print(f"{'='*50}")
        
        print(f"\n📹 Video Configuration:")
        print(f"  Camera Index: {cls.CAMERA_INDEX}")
        print(f"  Frame Size: {cls.FRAME_WIDTH}x{cls.FRAME_HEIGHT}")
        print(f"  FPS: {cls.FPS}")
        
        print(f"\n🤖 AI Model Configuration:")
        print(f"  YOLO Model: {cls.YOLO_MODEL_PATH}")
        print(f"  Face Detection Confidence: {cls.MEDIAPIPE_FACE_DETECTION_CONFIDENCE}")
        print(f"  Face Mesh Confidence: {cls.MEDIAPIPE_FACE_MESH_CONFIDENCE}")
        
        print(f"\n👁️ Face Movement Configuration:")
        print(f"  Movement Threshold: {cls.FACE_MOVEMENT_THRESHOLD}s")
        print(f"  Movement Sensitivity: {cls.FACE_MOVEMENT_SENSITIVITY}px")
        print(f"  History Size: {cls.FACE_MOVEMENT_HISTORY_SIZE} frames")
        
        print(f"\n🔊 Sound Detection Configuration:")
        print(f"  High Amplitude Threshold: {cls.SOUND_AMPLITUDE_THRESHOLDS['high']}")
        print(f"  Medium Amplitude Threshold: {cls.SOUND_AMPLITUDE_THRESHOLDS['medium']}")
        print(f"  Whispering Count Threshold: {cls.SOUND_DETECTION_COUNTS['whispering']}")
        
        print(f"\n⏱️ Time Thresholds:")
        for name, value in cls.TIME_THRESHOLDS.items():
            print(f"  {name.replace('_', ' ').title()}: {value}s")
            
        print(f"\n📊 Score Penalties:")
        for name, value in cls.SCORE_PENALTIES.items():
            print(f"  {name.replace('_', ' ').title()}: {value} points")
            
        print(f"\n🚫 Forbidden Objects ({len(cls.FORBIDDEN_OBJECTS)}):")
        for obj in cls.FORBIDDEN_OBJECTS:
            print(f"  - {obj}")
            
        print(f"\n📝 Logging Configuration:")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Log File: {cls.LOG_FILE}")
        print(f"  Max Log Size: {cls.LOG_MAX_SIZE}MB")
        
        print(f"\n⚙️ Performance Configuration:")
        print(f"  Frame Processing Interval: {cls.FRAME_PROCESSING_INTERVAL}s")
        print(f"  Audio Processing Interval: {cls.AUDIO_PROCESSING_INTERVAL}s")
        
        print(f"\n🔒 Security Configuration:")
        print(f"  Encryption Enabled: {cls.ENABLE_ENCRYPTION}")
        print(f"  Desktop Notifications: {cls.ENABLE_DESKTOP_NOTIFICATIONS}")
        
        print(f"\n{'='*50}\n")

# Create configuration instance
config = Config()

if __name__ == "__main__":
    # Validate and print configuration
    is_valid, errors = config.validate_config()
    
    if is_valid:
        config.print_config()
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
