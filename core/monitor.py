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

from detectors import (
    FaceDetector, ObjectDetector, AudioDetector,
    HandDetector, EyeTracker, PostureDetector, BehaviorAnalyzer
)
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
        self.hand_detector = HandDetector(self.config)
        self.eye_tracker = EyeTracker(self.config)
        self.posture_detector = PostureDetector(self.config)
        self.behavior_analyzer = BehaviorAnalyzer(self.config)
        
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
        self.frame_skip = 1  # Process every frame
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
    
    def process_frame(self, frame):
        """Process frame with optimized detection and new features"""
        self.frame_skip_count += 1
        
        # Update FPS
        self._update_fps()
        
        # Process face detection (always needed)
        detection_results = self.face_detector.process(frame)
        
        # Prepare detection data for behavior analysis
        detection_data = {}
        
        # === BASIC DETECTIONS ===
        # Face detection checks
        if self.face_detector.detect_face_away(detection_results['face']):
            self.alert_manager.add_alert("Student looking away", "face_away", self.notification_system)
            detection_data['looking_away'] = True
        
        if self.face_detector.detect_person_absence(detection_results['pose']):
            self.alert_manager.add_alert("Student not present", "person_absent", self.notification_system)
        
        if self.face_detector.detect_multiple_people(detection_results['pose']):
            self.alert_manager.add_alert("Multiple people detected", "multiple_people", self.notification_system)
        
        # === ADVANCED DETECTIONS ===
        face_landmarks = None
        if detection_results['face_mesh'].multi_face_landmarks:
            face_landmarks = detection_results['face_mesh'].multi_face_landmarks[0]
            
            # Face movement
            direction = self.face_detector.detect_face_movement(face_landmarks, frame)
            if direction:
                self.alert_manager.add_alert(
                    f"Face looking {direction} for {self.face_detector.face_movement_threshold}s",
                    "face_movement",
                    self.notification_system
                )
                detection_data['rapid_movement'] = True
            
            # Eye gaze tracking (NEW)
            gaze_data = self.eye_tracker.track_gaze(face_landmarks, frame.shape)
            if gaze_data:
                if self.eye_tracker.detect_prolonged_looking_away(gaze_data):
                    self.alert_manager.add_alert(
                        "Prolonged looking away from screen",
                        "face_away",
                        self.notification_system
                    )
                    detection_data['looking_away'] = True
            
            # Draw face mesh
            self.face_detector.draw_landmarks(frame, detection_results['face_mesh'], detection_results['pose'])
        
        # Hand detection (NEW)
        if self.frame_skip_count % 2 == 0:  # Every 2nd frame
            hand_results = self.hand_detector.process(frame)
            if hand_results.multi_hand_landmarks:
                # Detect suspicious hand movements
                if self.hand_detector.detect_suspicious_hand_movements(hand_results, face_landmarks):
                    self.alert_manager.add_alert(
                        "Suspicious hand movement detected (possible phone usage)",
                        "suspicious_behavior",
                        self.notification_system
                    )
                    detection_data['hand_near_face'] = True
                
                # Detect typing pattern
                if self.hand_detector.detect_typing_pattern(hand_results):
                    self.alert_manager.add_alert(
                        "Typing pattern detected (possible phone/device usage)",
                        "suspicious_behavior",
                        self.notification_system
                    )
                
                # Draw hands
                self.hand_detector.draw_hands(frame, hand_results)
        
        # Posture detection (NEW)
        if detection_results['pose'].pose_landmarks:
            posture_data = self.posture_detector.detect_posture(
                detection_results['pose'].pose_landmarks,
                frame.shape
            )
            if posture_data and posture_data.get('suspicious'):
                self.alert_manager.add_alert(
                    "Suspicious posture detected",
                    "suspicious_behavior",
                    self.notification_system
                )
                detection_data['posture_change'] = True
        
        # Object detection (with frame skipping)
        if self.frame_skip_count % self.frame_skip == 0:
            objects_detected = self.object_detector.detect(frame)
            if objects_detected:
                self.object_detector.draw_detections(frame, objects_detected)
                self.alert_manager.add_object_alert(objects_detected, self.notification_system)
                detection_data['object_detected'] = True
        
        # Emotion detection (optional, heavier)
        if self.emotion_detector and face_landmarks and self.frame_skip_count % 3 == 0:
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
        
        # === BEHAVIOR ANALYSIS (NEW) ===
        behavior_analysis = self.behavior_analyzer.analyze_pattern(detection_data)
        if behavior_analysis['risk_level'] == 'high':
            risk_summary = self.behavior_analyzer.get_risk_summary()
            if risk_summary:
                self.alert_manager.add_alert(
                    f"High risk behavior detected (Risk Score: {risk_summary['current_risk']})",
                    "high_risk_behavior",
                    self.notification_system
                )
        
        # Draw overlays
        self._draw_overlays(frame, behavior_analysis)
        
        # Update termination
        if self.alert_manager.update_exam_termination():
            if self.alert_manager.should_terminate():
                self._terminate_exam()
        
        return frame
    
    def _update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:  # Update every second
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _draw_overlays(self, frame, behavior_analysis=None):
        """Draw UI overlays with enhanced information"""
        # Score with risk level
        score_text = f"Cheating Score: {self.alert_manager.cheating_score}/100"
        score_color = (0, 0, 255) if self.alert_manager.cheating_score > 50 else (0, 255, 0)
        cv2.putText(frame, score_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 3)
        
        # Risk level (NEW)
        if behavior_analysis:
            risk_level = behavior_analysis['risk_level']
            risk_colors = {
                'high': (0, 0, 255),
                'medium': (0, 165, 255),
                'low': (0, 255, 255),
                'normal': (0, 255, 0)
            }
            risk_color = risk_colors.get(risk_level, (255, 255, 255))
            risk_text = f"Risk Level: {risk_level.upper()} ({behavior_analysis['risk_score']})"
            cv2.putText(frame, risk_text, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, risk_color, 2)
        
        # FPS (NEW)
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, (frame.shape[1] - 150, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Alerts
        y_offset = 130
        for i, alert in enumerate(self.alert_manager.alerts[-3:]):
            cv2.putText(frame, f"⚠️ {alert}", (20, y_offset + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Status panel (enhanced)
        panel_y = frame.shape[0] - 120
        cv2.rectangle(frame, (10, panel_y), (400, frame.shape[0] - 10), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, panel_y), (400, frame.shape[0] - 10), (255, 255, 255), 2)
        
        # Audio status
        audio_status = "ON" if self.audio_detector.audio_monitoring else "OFF"
        audio_color = (0, 255, 0) if self.audio_detector.audio_monitoring else (0, 0, 255)
        cv2.putText(frame, f"Audio: {audio_status}", (20, panel_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, audio_color, 2)
        
        # Violations
        cv2.putText(frame, f"Violations: {self.alert_manager.real_time_metrics['object_violations']}",
                   (20, panel_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Behavior patterns (NEW)
        if behavior_analysis and behavior_analysis.get('patterns'):
            patterns_text = f"Patterns: {', '.join(behavior_analysis['patterns'][:2])}"
            cv2.putText(frame, patterns_text, (20, panel_y + 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
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
        print("   - Hand movement tracking (NEW)")
        print("   - Eye gaze tracking (NEW)")
        print("   - Posture detection (NEW)")
        print("   - Advanced behavior analysis (NEW)")
        if NEW_MODULES_AVAILABLE:
            print("   - Emotion detection")
        print("\n🚀 Performance Optimizations:")
        print("   - Adaptive frame skipping")
        print("   - Result caching")
        print("   - GPU acceleration")
        print("   - Parallel processing")
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

