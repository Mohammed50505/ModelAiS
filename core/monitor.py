"""
Main Exam Monitoring System
نظام المراقبة الرئيسي
"""

import cv2
import numpy as np
import time
import json
from datetime import datetime

# Import modules
try:
    from config import Config
except ImportError:
    Config = None

from detectors import FaceDetector, ObjectDetector, AudioDetector
from utils import setup_logger, AlertManager

# Optional modules
try:
    from emotion_detection import EmotionDetector
    from notification_system import NotificationSystem
    NEW_MODULES_AVAILABLE = True
except ImportError:
    NEW_MODULES_AVAILABLE = False


class ExamMonitor:
    """Optimized exam monitoring system"""
    
    def __init__(self):
        """Initialize monitoring system"""
        self.config = Config if Config else None
        self.logger = setup_logger()
        
        # Initialize detectors
        self.face_detector = FaceDetector(self.config)
        self.object_detector = ObjectDetector(self.config)
        self.audio_detector = AudioDetector(self.config)
        
        # Initialize alert manager
        self.alert_manager = AlertManager(self.config)
        
        # Optional modules
        if NEW_MODULES_AVAILABLE:
            self.emotion_detector = EmotionDetector()
            self.notification_system = NotificationSystem()
        else:
            self.emotion_detector = None
            self.notification_system = None
        
        # Initialize camera
        camera_idx = self.config.CAMERA_INDEX if self.config else 0
        self.cap = cv2.VideoCapture(camera_idx)
        if not self.cap.isOpened():
            self.logger.error("Could not open webcam")
            exit(1)
        
        frame_width = self.config.FRAME_WIDTH if self.config else 1280
        frame_height = self.config.FRAME_HEIGHT if self.config else 720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        print(f"📹 Camera: {frame_width}x{frame_height}")
        
        # Session tracking
        self.session_start_time = time.time()
        
        # Frame processing optimization
        self.frame_skip_count = 0
        self.frame_skip = 1  # Process every frame (can be increased for more speed)
    
    def process_frame(self, frame):
        """Process frame with optimized detection"""
        self.frame_skip_count += 1
        
        # Convert to RGB once
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process face detection (always needed for display)
        detection_results = self.face_detector.process(frame)
        
        # Run detections (with frame skipping for heavy operations)
        if self.frame_skip_count % self.frame_skip == 0:
            # Object detection (heavier, skip some frames)
            objects_detected = self.object_detector.detect(frame)
            if objects_detected:
                self.object_detector.draw_detections(frame, objects_detected)
                self.alert_manager.add_object_alert(objects_detected, self.notification_system)
        
        # Face detection checks (lighter, run more often)
        if self.face_detector.detect_face_away(detection_results['face']):
            self.alert_manager.add_alert("Student looking away", "face_away", self.notification_system)
        
        if self.face_detector.detect_person_absence(detection_results['pose']):
            self.alert_manager.add_alert("Student not present", "person_absent", self.notification_system)
        
        if self.face_detector.detect_multiple_people(detection_results['pose']):
            self.alert_manager.add_alert("Multiple people detected", "multiple_people", self.notification_system)
        
        # Face movement (if mesh available)
        if detection_results['face_mesh'].multi_face_landmarks:
            face_landmarks = detection_results['face_mesh'].multi_face_landmarks[0]
            direction = self.face_detector.detect_face_movement(face_landmarks, frame)
            if direction:
                self.alert_manager.add_alert(
                    f"Face looking {direction} for {self.face_detector.face_movement_threshold}s",
                    "face_movement",
                    self.notification_system
                )
            
            # Draw face mesh
            self.face_detector.draw_landmarks(frame, detection_results['face_mesh'], detection_results['pose'])
            
            # Emotion detection (optional, heavier)
            if self.emotion_detector and self.frame_skip_count % 3 == 0:  # Every 3rd frame
                try:
                    emotion_results = self.emotion_detector.detect_emotion(frame, face_landmarks)
                    if emotion_results and emotion_results.get('suspicious', False):
                        if emotion_results.get('suspicious_score', 0) > 0.7:
                            self.alert_manager.add_alert(
                                f"Suspicious emotion: {emotion_results.get('emotion', 'unknown')}",
                                "suspicious_emotion",
                                self.notification_system
                            )
                except Exception:
                    pass
        
        # Draw overlays
        self._draw_overlays(frame)
        
        # Update termination
        if self.alert_manager.update_exam_termination():
            if self.alert_manager.should_terminate():
                self._terminate_exam()
        
        return frame
    
    def _draw_overlays(self, frame):
        """Draw UI overlays"""
        # Score
        score_text = f"Cheating Score: {self.alert_manager.cheating_score}/100"
        score_color = (0, 0, 255) if self.alert_manager.cheating_score > 50 else (0, 255, 0)
        cv2.putText(frame, score_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 3)
        
        # Alerts
        y_offset = 100
        for i, alert in enumerate(self.alert_manager.alerts[-3:]):
            cv2.putText(frame, f"⚠️ {alert}", (20, y_offset + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Status
        status_y = frame.shape[0] - 50
        audio_status = "ON" if self.audio_detector.audio_monitoring else "OFF"
        cv2.putText(frame, f"Audio: {audio_status}", (20, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Metrics
        metrics_y = frame.shape[0] - 80
        cv2.putText(frame, f"Violations: {self.alert_manager.real_time_metrics['object_violations']}",
                   (20, metrics_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Termination warning
        if self.alert_manager.exam_termination_countdown and self.alert_manager.exam_termination_countdown > 0:
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
            warning_text = f"🚨 EXAM WILL CLOSE IN {self.alert_manager.exam_termination_countdown:.1f}s!"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            cv2.putText(frame, warning_text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4)
    
    def _terminate_exam(self):
        """Terminate exam"""
        print("🚨 EXAM TERMINATED!")
        self.save_final_report()
        self.cleanup()
        exit(0)
    
    def save_final_report(self):
        """Save final report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'final_score': self.alert_manager.cheating_score,
                'total_violations': sum(self.alert_manager.real_time_metrics.values()),
                'incidents': self.alert_manager.cheating_incidents,
                'exam_duration': time.time() - self.session_start_time,
                'metrics': self.alert_manager.real_time_metrics.copy()
            }
            
            filename = f"exam_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Report saved: {filename}")
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
    
    def run(self):
        """Main monitoring loop"""
        print("=" * 60)
        print("🎓 Advanced AI Exam Monitoring System")
        print("=" * 60)
        print("📋 Controls:")
        print("   - Press 'q' to quit")
        print("   - Press 'a' to toggle audio")
        print("\n✨ Features:")
        print("   - Fast face detection")
        print("   - Optimized object detection (YOLO)")
        print("   - Audio monitoring")
        if NEW_MODULES_AVAILABLE:
            print("   - Emotion detection")
        print("=" * 60)
        
        # Start audio monitoring
        self.audio_detector.start_monitoring(
            alert_callback=lambda msg, atype: self.alert_manager.add_alert(msg, atype, self.notification_system)
        )
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Could not read frame")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display
                cv2.imshow('AI Exam Monitor', processed_frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('a'):
                    if self.audio_detector.audio_monitoring:
                        self.audio_detector.stop_monitoring()
                        print("🔇 Audio OFF")
                    else:
                        self.audio_detector.start_monitoring(
                            alert_callback=lambda msg, atype: self.alert_manager.add_alert(msg, atype, self.notification_system)
                        )
                        print("🔊 Audio ON")
        
        except KeyboardInterrupt:
            print("\n⏹️ Stopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n" + "=" * 60)
        print("🛑 Shutting down...")
        
        self.audio_detector.stop_monitoring()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        print("\n📊 Final Statistics:")
        print(f"   Score: {self.alert_manager.cheating_score}/100")
        print(f"   Duration: {time.time() - self.session_start_time:.1f}s")
        print(f"   Incidents: {len(self.alert_manager.cheating_incidents)}")
        print(f"   Violations: {self.alert_manager.real_time_metrics['object_violations']}")
        print("=" * 60)


if __name__ == "__main__":
    monitor = ExamMonitor()
    monitor.run()

