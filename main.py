import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import logging
import json
from datetime import datetime
from ultralytics import YOLO
import speech_recognition as sr
import pyaudio
import wave
import os
from collections import deque
import math

# Import new modules
try:
    from emotion_detection import EmotionDetector
    from notification_system import NotificationSystem
    NEW_MODULES_AVAILABLE = True
    print("✅ Advanced modules loaded successfully")
except ImportError:
    print("⚠️ Some advanced modules not available, using basic features only")
    NEW_MODULES_AVAILABLE = False

class AdvancedExamMonitor:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize face detection and mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        
        # Initialize face mesh for detailed facial landmarks
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize pose detection
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize YOLO model for object detection
        self.yolo_model = YOLO('yolov8n.pt')
        
        # Initialize new systems if available
        if NEW_MODULES_AVAILABLE:
            self.emotion_detector = EmotionDetector()
            self.notification_system = NotificationSystem()
            print("✅ Advanced modules loaded: Emotion detection, Notifications")
        else:
            self.emotion_detector = None
            self.notification_system = None
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            exit()
        
        # Set webcam properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Initialize variables
        self.cheating_score = 0
        self.alerts = []
        self.last_face_time = time.time()
        self.last_person_time = time.time()
        self.face_away_start = None
        self.person_absent_start = None
        self.talking_start = None
        
        # New cheating detection variables
        self.student_data = {}
        self.cheating_incidents = []
        self.real_time_metrics = {
            'face_movements': 0,
            'audio_violations': 0,
            'object_violations': 0,
            'communication_attempts': 0,
            'suspicious_behavior': 0
        }
        self.session_start_time = time.time()
        self.last_alert_time = 0
        self.alert_cooldown = 5  # seconds between alerts
        
        # Exam termination system
        self.exam_termination_countdown = None
        self.exam_termination_start = None
        self.exam_termination_duration = 10  # seconds
        self.exam_terminated = False
        
        # Dashboard control
        self.dashboard_control = {
            'is_running': False,
            'current_student': None,
            'exam_start_time': None,
            'exam_duration': 0
        }
        
        # Face movement tracking
        self.face_movement_start = None
        self.face_movement_direction = None
        self.face_movement_threshold = 6.0  # 3 seconds
        self.face_center_history = deque(maxlen=30)  # Store last 30 frames
        self.face_movement_sensitivity = 50  # pixels threshold for movement
        
        # Audio monitoring with enhanced recognition
        self.audio_recognizer = sr.Recognizer()
        self.audio_monitoring = False
        self.audio_thread = None
        self.detected_sounds = []
        self.sound_patterns = {
            'whispering': 0,
            'talking': 0,
            'keyboard_typing': 0,
            'paper_rustling': 0,
            'phone_vibration': 0,
            'other_sounds': 0
        }
        
        # Initialize logging
        self.setup_logging()
        
        # Load forbidden objects (phones, books, etc.)
        # Forbidden Objects - Extended for Exam Cheating Detection
        self.forbidden_objects = [
            'cell phone', 'smartphone', 'mobile phone', 'phone',
            'laptop', 'computer', 'tablet', 'ipad', 'notebook',
            'headphone', 'earphone', 'airpods', 'earbuds',
            'smartwatch', 'watch', 'fitness tracker', 'band',
            'calculator', 'scientific calculator', 'calc',
            'book', 'notebook', 'paper', 'note', 'textbook',
            'camera', 'webcam', 'microphone', 'mic',
            'usb', 'memory stick', 'flash drive', 'pen drive',
            'glasses', 'sunglasses', 'eye wear'
        ]
        
        # Time thresholds
        self.FACE_AWAY_THRESHOLD = 5.0  # seconds
        self.PERSON_ABSENT_THRESHOLD = 3.0  # seconds
        self.TALKING_THRESHOLD = 2.0  # seconds
        
        # Score penalties
        self.SCORE_PENALTIES = {
            'multiple_people': 20,
            'face_away': 10,
            'forbidden_object': 25,
            'person_absent': 15,
            'talking': 20,
            'face_movement': 15,  # New penalty for face movement
            'suspicious_sounds': 15,  # New penalty for suspicious sounds
            'suspicious_emotion': 20  # New penalty for suspicious emotions
        }
        
        # Alert history
        self.alert_history = deque(maxlen=10)
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('cheating_log.txt'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_audio_monitoring(self):
        """Start audio monitoring in a separate thread"""
        self.audio_monitoring = True
        self.audio_thread = threading.Thread(target=self.monitor_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def stop_audio_monitoring(self):
        """Stop audio monitoring"""
        self.audio_monitoring = False
        if self.audio_thread:
            self.audio_thread.join()
            
    def monitor_audio(self):
        """Enhanced audio monitoring for various sound patterns"""
        try:
            with sr.Microphone() as source:
                self.audio_recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.audio_monitoring:
                    try:
                        audio = self.audio_recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        # Analyze audio characteristics
                        audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                        
                        # Detect sound patterns
                        self.analyze_sound_patterns(audio_data)
                        
                        # Try to recognize speech
                        try:
                            text = self.audio_recognizer.recognize_google(audio)
                            if text.strip():
                                self.detect_talking()
                                print(f"Detected speech: {text}")
                        except sr.UnknownValueError:
                            pass
                        except Exception as e:
                            print(f"Speech recognition error: {e}")
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Audio monitoring error: {e}")
            
    def analyze_sound_patterns(self, audio_data):
        """Analyze audio data for various sound patterns"""
        if len(audio_data) == 0:
            return
            
        # Calculate audio characteristics
        rms = np.sqrt(np.mean(audio_data**2))
        zero_crossings = np.sum(np.diff(np.sign(audio_data)))
        
        # Detect different sound types based on characteristics
        if rms > 1000:  # High amplitude
            if zero_crossings > 1000:  # High frequency
                self.sound_patterns['keyboard_typing'] += 1
                if self.sound_patterns['keyboard_typing'] > 5:
                    self.add_alert("Suspicious keyboard activity detected", "suspicious_sounds")
                    self.sound_patterns['keyboard_typing'] = 0
            else:  # Low frequency
                self.sound_patterns['talking'] += 1
                if self.sound_patterns['talking'] > 3:
                    self.add_alert("Suspicious talking detected", "talking")
                    self.sound_patterns['talking'] = 0
        elif rms > 500:  # Medium amplitude
            if zero_crossings < 100:  # Low frequency
                self.sound_patterns['whispering'] += 1
                if self.sound_patterns['whispering'] > 5:
                    self.add_alert("Whispering detected", "suspicious_sounds")
                    self.sound_patterns['whispering'] = 0
            else:
                self.sound_patterns['paper_rustling'] += 1
                if self.sound_patterns['paper_rustling'] > 8:
                    self.add_alert("Paper rustling detected", "suspicious_sounds")
                    self.sound_patterns['paper_rustling'] = 0
            
    def detect_talking(self):
        """Detect suspicious talking"""
        current_time = time.time()
        
        if self.talking_start is None:
            self.talking_start = current_time
        elif current_time - self.talking_start > self.TALKING_THRESHOLD:
            self.add_alert("Suspicious talking detected", "talking")
            self.talking_start = None
            
    def detect_face_movement(self, face_landmarks, frame):
        """Detect face movement in different directions"""
        if not face_landmarks:
            return
            
        try:
            # Get face center point (nose tip) - MediaPipe Face Mesh has 468 landmarks
            # Nose tip is around landmark 4
            nose_tip = face_landmarks.landmark[4]  # Access landmark properly
            face_center = (int(nose_tip.x * frame.shape[1]), int(nose_tip.y * frame.shape[0]))
            
            # Store face center history
            self.face_center_history.append(face_center)
            
            if len(self.face_center_history) < 10:
                return
                
            # Calculate movement direction
            start_point = self.face_center_history[0]
            end_point = self.face_center_history[-1]
            
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            
            # Determine movement direction
            direction = None
            if abs(dx) > self.face_movement_sensitivity:
                if dx > 0:
                    direction = "right"
                else:
                    direction = "left"
            elif abs(dy) > self.face_movement_sensitivity:
                if dy > 0:
                    direction = "down"
                else:
                    direction = "up"
                    
            if direction:
                if self.face_movement_direction != direction:
                    self.face_movement_direction = direction
                    self.face_movement_start = time.time()
                elif self.face_movement_start and time.time() - self.face_movement_start > self.face_movement_threshold:
                    self.add_alert(f"Face looking {direction} for {self.face_movement_threshold} seconds", "face_movement")
                    self.face_movement_start = None
                    
        except Exception as e:
            print(f"Face movement detection error: {e}")
            return
                
    def detect_emotions(self, face_landmarks, frame):
        """Detect emotions using the emotion detector"""
        if not face_landmarks or not self.emotion_detector:
            return None
            
        try:
            # Detect emotions
            emotion_results = self.emotion_detector.detect_emotion(frame, face_landmarks)
            
            # Check for suspicious emotions
            if emotion_results.get('suspicious', False):
                suspicious_score = emotion_results.get('suspicious_score', 0)
                if suspicious_score > 0.7:
                    self.add_alert(f"Suspicious emotional behavior detected: {emotion_results.get('emotion', 'unknown')}", "suspicious_emotion")
                    
                    # Send notification for suspicious emotions
                    if self.notification_system:
                        self.notification_system.send_notification(
                            'emotion_suspicious',
                            f"High suspicious emotion detected: {emotion_results.get('emotion', 'unknown')}",
                            emotion_results,
                            'medium'
                        )
            
            return emotion_results
            
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return None
            
    def detect_multiple_people(self, pose_results):
        """Detect if multiple people are in the frame"""
        if pose_results.pose_landmarks:
            # Count visible pose landmarks to estimate number of people
            landmarks = pose_results.pose_landmarks.landmark
            visible_landmarks = sum(1 for lm in landmarks if lm.visibility > 0.5)
            
            # If we have too many visible landmarks, likely multiple people
            if visible_landmarks > 33:  # Normal person has 33 landmarks
                self.add_alert("Multiple people detected", "multiple_people")
                return True
        return False
        
    def detect_face_away(self, face_results, frame):
        """Detect if student is looking away from screen"""
        current_time = time.time()
        
        if face_results.detections:
            self.last_face_time = current_time
            if self.face_away_start:
                self.face_away_start = None
        else:
            if self.face_away_start is None:
                self.face_away_start = current_time
            elif current_time - self.face_away_start > self.FACE_AWAY_THRESHOLD:
                self.add_alert("Student looking away", "face_away")
                self.face_away_start = None
                
    def detect_forbidden_objects(self, frame):
        """Detect forbidden objects using YOLO with advanced cheating detection"""
        try:
            results = self.yolo_model(frame, verbose=False)
            objects_detected = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0]
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = result.names[cls]
                        
                        if class_name in self.forbidden_objects and conf > 0.5:
                            # Draw bounding box with different colors based on severity
                            color = (0, 0, 255)  # Red for high severity
                            if class_name in ['cell phone', 'smartphone', 'laptop']:
                                color = (0, 0, 255)  # Red
                            elif class_name in ['book', 'notebook', 'paper']:
                                color = (0, 165, 255)  # Orange
                            else:
                                color = (0, 255, 255)  # Yellow
                            
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                            cv2.putText(frame, f"{class_name} {conf:.2f}", (int(x1), int(y1) - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            
                            objects_detected.append({
                                'name': class_name,
                                'confidence': float(conf),
                                'position': (int(x1), int(y1), int(x2), int(y2)),
                                'severity': 'high' if class_name in ['cell phone', 'smartphone', 'laptop'] else 'medium'
                            })
                            
                            # Update metrics
                            self.real_time_metrics['object_violations'] += 1
            
            # Add alert if objects detected
            if objects_detected:
                self.add_advanced_alert("forbidden_object", objects_detected)
                return True
                
        except Exception as e:
            print(f"YOLO detection error: {e}")
        return False
        
    def detect_person_absence(self, pose_results):
        """Detect if student is not present in frame"""
        current_time = time.time()
        
        if pose_results.pose_landmarks:
            self.last_person_time = current_time
            if self.person_absent_start:
                self.person_absent_start = None
        else:
            if self.person_absent_start is None:
                self.person_absent_start = current_time
            elif current_time - self.person_absent_start > self.PERSON_ABSENT_THRESHOLD:
                self.add_alert("Student not present", "person_absent")
                self.person_absent_start = None
                
    def add_alert(self, message, alert_type):
        """Add a new alert and update cheating score"""
        current_time = time.time()
        
        # Check cooldown to prevent spam
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert = f"[{timestamp}] {message}"
        
        if alert not in self.alert_history:
            self.alerts.append(alert)
            self.alert_history.append(alert)
            
            # Update cheating score
            if alert_type in self.SCORE_PENALTIES:
                self.cheating_score = min(100, self.cheating_score + self.SCORE_PENALTIES[alert_type])
                
            # Check for exam termination
            if self.cheating_score >= 100 and not self.exam_termination_countdown:
                self.start_exam_termination()
                
            # Log the alert
            print(f"ALERT: {message}")
            
            # Update real-time metrics
            self.update_metrics(alert_type)
            
            # Send notification based on alert type
            if self.notification_system:
                priority = 'medium'
                if alert_type in ['forbidden_object', 'multiple_people']:
                    priority = 'high'
                elif alert_type in ['system_error']:
                    priority = 'critical'
                    
                self.notification_system.send_notification(
                    alert_type,
                    message,
                    {'timestamp': timestamp, 'score': self.cheating_score},
                    priority
                )
            
            # Keep only recent alerts
            if len(self.alerts) > 5:
                self.alerts.pop(0)
                
            self.last_alert_time = current_time
    
    def add_advanced_alert(self, alert_type, data):
        """Add advanced alert with detailed data"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if alert_type == "forbidden_object":
            for obj in data:
                message = f"Unauthorized object detected: {obj['name']} (Confidence: {obj['confidence']:.2f})"
                self.add_alert(message, "forbidden_object")
                
                # Log detailed incident
                incident = {
                    'timestamp': timestamp,
                    'type': alert_type,
                    'object': obj['name'],
                    'confidence': obj['confidence'],
                    'severity': obj['severity'],
                    'position': obj['position']
                }
                self.cheating_incidents.append(incident)
        
        self.last_alert_time = current_time
    
    def update_metrics(self, alert_type):
        """Update real-time metrics based on alert type"""
        if alert_type == "face_movement":
            self.real_time_metrics['face_movements'] += 1
        elif alert_type == "talking":
            self.real_time_metrics['audio_violations'] += 1
        elif alert_type == "forbidden_object":
            self.real_time_metrics['object_violations'] += 1
        elif alert_type == "multiple_people":
            self.real_time_metrics['communication_attempts'] += 1
        elif alert_type in ["face_away", "person_absent"]:
            self.real_time_metrics['suspicious_behavior'] += 1
    
    def start_exam_termination(self):
        """Start exam termination countdown"""
        if not self.exam_termination_countdown:
            self.exam_termination_countdown = self.exam_termination_duration
            self.exam_termination_start = time.time()
            print("🚨 EXAM TERMINATION INITIATED! Cheating score reached 100!")
            print(f"⏰ Exam will close in {self.exam_termination_duration} seconds")
    
    def update_exam_termination(self):
        """Update exam termination countdown"""
        if self.exam_termination_countdown and self.exam_termination_countdown > 0:
            elapsed = time.time() - self.exam_termination_start
            self.exam_termination_countdown = max(0, self.exam_termination_duration - elapsed)
            
            if self.exam_termination_countdown <= 0:
                self.terminate_exam()
    
    def terminate_exam(self):
        """Terminate the exam"""
        self.exam_terminated = True
        print("🚨 EXAM TERMINATED! Student disqualified due to cheating!")
        
        # Save final report
        self.save_final_report()
        
        # Stop monitoring
        self.cleanup()
        exit(0)
    
    def save_final_report(self):
        """Save final exam report"""
        try:
            final_report = {
                'timestamp': datetime.now().isoformat(),
                'student': self.dashboard_control.get('current_student', 'Unknown'),
                'final_score': self.cheating_score,
                'total_violations': sum(self.real_time_metrics.values()),
                'incidents': self.cheating_incidents,
                'exam_duration': time.time() - self.session_start_time,
                'termination_reason': 'Cheating score reached 100'
            }
            
            with open('final_exam_report.json', 'w') as f:
                json.dump(final_report, f, indent=2)
                
            print("📄 Final exam report saved to final_exam_report.json")
            
        except Exception as e:
            print(f"Error saving final report: {e}")
    
    # Dashboard control methods
    def start_monitoring(self, student_name=None):
        """Start monitoring from dashboard"""
        self.dashboard_control['is_running'] = True
        self.dashboard_control['current_student'] = student_name
        self.dashboard_control['exam_start_time'] = time.time()
        self.session_start_time = time.time()
        print(f"🎯 Monitoring started for student: {student_name or 'Unknown'}")
        print(f"⏰ Exam start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Save dashboard data immediately
        self.save_dashboard_data()
    
    def stop_monitoring(self):
        """Stop monitoring from dashboard"""
        self.dashboard_control['is_running'] = False
        self.dashboard_control['exam_start_time'] = None
        print("⏹️ Monitoring stopped by dashboard")
        print(f"⏰ Exam duration: {time.time() - self.session_start_time:.1f} seconds")
        
        # Save dashboard data immediately
        self.save_dashboard_data()
    
    def add_student(self, student_id, student_name):
        """Add new student"""
        self.student_data[student_id] = {
            'name': student_name,
            'id': student_id,
            'added_at': datetime.now().isoformat(),
            'status': 'active'
        }
        print(f"👤 Student added: {student_name} (ID: {student_id})")
        
        # Save dashboard data immediately
        self.save_dashboard_data()
    
    def remove_student(self, student_id):
        """Remove student"""
        if student_id in self.student_data:
            student_name = self.student_data[student_id]['name']
            del self.student_data[student_id]
            print(f"🗑️ Student removed: {student_name} (ID: {student_id})")
            
            # Save dashboard data immediately
            self.save_dashboard_data()
            return True
        return False
    
    def save_dashboard_data(self):
        """Save data for dashboard integration"""
        try:
            # Calculate exam duration if exam is running
            exam_duration = 0
            if self.dashboard_control['exam_start_time'] and self.dashboard_control['is_running']:
                exam_duration = time.time() - self.dashboard_control['exam_start_time']
            
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'cheating_score': self.cheating_score,
                'real_time_metrics': self.real_time_metrics.copy(),
                'current_alerts': len(self.alerts),
                'session_duration': time.time() - self.session_start_time,
                'incidents_count': len(self.cheating_incidents),
                'dashboard_control': {
                    'is_running': self.dashboard_control['is_running'],
                    'current_student': self.dashboard_control['current_student'],
                    'exam_start_time': self.dashboard_control['exam_start_time'],
                    'exam_duration': exam_duration
                },
                'exam_termination': {
                    'countdown': self.exam_termination_countdown,
                    'terminated': self.exam_terminated
                },
                'students': list(self.student_data.values())
            }
            
            # Save to JSON file for dashboard
            with open('dashboard_data.json', 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving dashboard data: {e}")
                
    def draw_face_mesh(self, frame, face_landmarks):
        """Draw face mesh and movement indicators"""
        if face_landmarks:
            try:
                # Draw face mesh
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )
                
                # Draw movement direction indicator
                if self.face_movement_direction and self.face_movement_start:
                    remaining_time = self.face_movement_threshold - (time.time() - self.face_movement_start)
                    if remaining_time > 0:
                        direction_text = f"Looking {self.face_movement_direction}: {remaining_time:.1f}s"
                        cv2.putText(frame, direction_text, (20, frame.shape[0] - 80), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            except Exception as e:
                print(f"Face mesh drawing error: {e}")
                return
                    
    def draw_emotion_overlay(self, frame, emotion_results):
        """Draw emotion information on frame"""
        if emotion_results:
            # Draw emotion box
            cv2.rectangle(frame, (frame.shape[1] - 300, 10), (frame.shape[1] - 10, 150), (0, 0, 0), -1)
            cv2.rectangle(frame, (frame.shape[1] - 300, 10), (frame.shape[1] - 10, 150), (255, 255, 255), 2)
            
            # Draw emotion text
            emotion_text = f"Emotion: {emotion_results.get('emotion', 'Unknown')}"
            confidence_text = f"Confidence: {emotion_results.get('confidence', 0):.2f}"
            suspicious_text = f"Suspicious: {'YES' if emotion_results.get('suspicious') else 'NO'}"
            
            cv2.putText(frame, emotion_text, (frame.shape[1] - 290, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, confidence_text, (frame.shape[1] - 290, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            suspicious_color = (0, 0, 255) if emotion_results.get('suspicious') else (0, 255, 0)
            cv2.putText(frame, suspicious_text, (frame.shape[1] - 290, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, suspicious_color, 2)
                
    def draw_bounding_box(self, frame, pose_results):
        """Draw bounding box around detected person"""
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            
            # Get frame dimensions
            h, w, _ = frame.shape
            
            # Find bounding box coordinates
            x_coords = [int(lm.x * w) for lm in landmarks if lm.visibility > 0.5]
            y_coords = [int(lm.y * h) for lm in landmarks if lm.visibility > 0.5]
            
            if x_coords and y_coords:
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Add padding
                padding = 50
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(w, x_max + padding)
                y_max = min(h, y_max + padding)
                
                # Draw green bounding box
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
                
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )
                
    def draw_overlays(self, frame):
        """Draw cheating score and alerts on frame"""
        # Draw cheating score
        score_text = f"Cheating Score: {self.cheating_score}/100"
        score_color = (0, 0, 255) if self.cheating_score > 50 else (0, 255, 0)
        cv2.putText(frame, score_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, score_color, 3)
        
        # Draw alerts
        y_offset = 100
        for i, alert in enumerate(self.alerts[-3:]):  # Show last 3 alerts
            cv2.putText(frame, f"⚠️ {alert}", (20, y_offset + i * 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        # Draw status indicators
        status_y = frame.shape[0] - 50
        cv2.putText(frame, "Audio Monitoring: ON" if self.audio_monitoring else "Audio Monitoring: OFF", 
                    (20, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw sound detection info
        sound_y = frame.shape[0] - 120
        cv2.putText(frame, f"Detected Sounds: {len([s for s in self.sound_patterns.values() if s > 0])}", 
                    (20, sound_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Draw real-time metrics
        metrics_y = frame.shape[0] - 150
        cv2.putText(frame, f"Face Movements: {self.real_time_metrics['face_movements']}", 
                    (20, metrics_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        metrics_y2 = frame.shape[0] - 180
        cv2.putText(frame, f"Object Violations: {self.real_time_metrics['object_violations']}", 
                    (20, metrics_y2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw exam termination warning - IMPROVED VERSION
        if self.exam_termination_countdown and self.exam_termination_countdown > 0:
            # Draw full screen red warning background
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
            
            # Draw warning text in center
            warning_text = f"🚨 EXAM WILL CLOSE IN {self.exam_termination_countdown:.1f} SECONDS!"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 4)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            
            cv2.putText(frame, warning_text, (text_x, text_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 4)
            
            # Draw countdown bar at bottom
            bar_height = 80
            bar_y = frame.shape[0] - bar_height - 20
            bar_width = int((self.exam_termination_countdown / self.exam_termination_duration) * frame.shape[1])
            
            # Background bar
            cv2.rectangle(frame, (0, bar_y), (frame.shape[1], bar_y + bar_height), (100, 100, 100), -1)
            # Progress bar
            cv2.rectangle(frame, (0, bar_y), (bar_width, bar_y + bar_height), (0, 255, 0), -1)
            # Border
            cv2.rectangle(frame, (0, bar_y), (frame.shape[1], bar_y + bar_height), (255, 255, 255), 3)
            
            # Draw countdown text
            countdown_text = f"Time Remaining: {self.exam_termination_countdown:.1f}s"
            countdown_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            countdown_x = (frame.shape[1] - countdown_size[0]) // 2
            countdown_y = bar_y + (bar_height + countdown_size[1]) // 2
            
            cv2.putText(frame, countdown_text, (countdown_x, countdown_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
                    
    def process_frame(self, frame):
        """Process a single frame for cheating detection"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        face_results = self.face_detection.process(rgb_frame)
        face_mesh_results = self.face_mesh.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        
        # Run cheating detection
        self.detect_multiple_people(pose_results)
        self.detect_face_away(face_results, frame)
        self.detect_forbidden_objects(frame)
        self.detect_person_absence(pose_results)
        
        # Detect face movement if face mesh is available
        if face_mesh_results.multi_face_landmarks:
            self.detect_face_movement(face_mesh_results.multi_face_landmarks[0], frame)
            self.draw_face_mesh(frame, face_mesh_results.multi_face_landmarks[0])
            
            # Detect emotions
            try:
                emotion_results = self.detect_emotions(face_mesh_results.multi_face_landmarks[0], frame)
                if emotion_results:
                    self.draw_emotion_overlay(frame, emotion_results)
            except Exception as e:
                print(f"Emotion detection error in process_frame: {e}")
        
        # Draw visual elements
        self.draw_bounding_box(frame, pose_results)
        self.draw_overlays(frame)
        
        # Update exam termination countdown
        self.update_exam_termination()
        
        # Save data for dashboard
        self.save_dashboard_data()
        
        return frame
        
    def run(self):
        """Main monitoring loop"""
        print("Starting Advanced AI Exam Monitoring System...")
        print("Press 'q' to quit, 'a' to toggle audio monitoring")
        print("Features: Face movement tracking, Enhanced audio detection, Advanced cheating detection")
        if NEW_MODULES_AVAILABLE:
            print("New Features: Emotion detection, Advanced notifications, PDF reports")
        else:
            print("Note: Some advanced features not available")
        
        print("🔄 Waiting for dashboard commands...")
        print("📱 Open the dashboard and click 'Start Monitoring' to begin")
        
        # Start audio monitoring
        self.start_audio_monitoring()
        
        try:
            while True:
                # Always check for dashboard commands first
                self.check_dashboard_commands()
                
                # Check if monitoring is controlled by dashboard
                if not self.dashboard_control['is_running']:
                    # Show waiting screen
                    waiting_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                    
                    # Draw waiting message
                    cv2.putText(waiting_frame, "WAITING FOR DASHBOARD COMMAND", 
                                (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
                    cv2.putText(waiting_frame, "Open dashboard and click 'Start Monitoring'", 
                                (250, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
                    cv2.putText(waiting_frame, "Press 'q' to quit", 
                                (500, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 150, 150), 2)
                    
                    # Show current status
                    status_text = f"Status: {'Running' if self.dashboard_control['is_running'] else 'Stopped'}"
                    cv2.putText(waiting_frame, status_text, (500, 450), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if self.dashboard_control['is_running'] else (0, 0, 255), 2)
                    
                    cv2.imshow('Advanced AI Exam Monitor', waiting_frame)
                    cv2.waitKey(1000)  # Wait 1 second
                    continue
                
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                    
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Display frame
                cv2.imshow('Advanced AI Exam Monitor', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('a'):
                    if self.audio_monitoring:
                        self.stop_audio_monitoring()
                        print("Audio monitoring disabled")
                    else:
                        self.start_audio_monitoring()
                        print("Audio monitoring enabled")
                        
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
        finally:
            self.cleanup()
    
    def check_dashboard_commands(self):
        """Check for dashboard commands and process them"""
        if os.path.exists('dashboard_commands.json'):
            try:
                with open('dashboard_commands.json', 'r') as f:
                    commands = json.load(f)
                
                if commands:  # Only process if there are commands
                    print(f"📥 Processing {len(commands)} dashboard command(s)...")
                    
                    for command in commands:
                        action = command.get('action')
                        print(f"🔄 Processing command: {action}")
                        
                        if action == 'start':
                            student_name = command.get('student_name', 'Unknown Student')
                            self.start_monitoring(student_name)
                            print(f"✅ Monitoring started for: {student_name}")
                            
                        elif action == 'stop':
                            self.stop_monitoring()
                            print("✅ Monitoring stopped")
                            
                        elif action == 'add_student':
                            student_id = command.get('student_id')
                            student_name = command.get('student_name')
                            if student_id and student_name:
                                self.add_student(student_id, student_name)
                                print(f"✅ Student added: {student_name} (ID: {student_id})")
                                
                        elif action == 'remove_student':
                            student_id = command.get('student_id')
                            if student_id:
                                if self.remove_student(student_id):
                                    print(f"✅ Student removed: {student_id}")
                                else:
                                    print(f"❌ Student not found: {student_id}")
                    
                    # Clear commands file after processing
                    os.remove('dashboard_commands.json')
                    print("🗑️ Commands file cleared")
                    
            except Exception as e:
                print(f"❌ Error processing dashboard commands: {e}")
                # Try to remove corrupted file
                try:
                    os.remove('dashboard_commands.json')
                    print("🗑️ Corrupted commands file removed")
                except:
                    pass
            
    def cleanup(self):
        """Clean up resources"""
        self.stop_audio_monitoring()
        self.cap.release()
        cv2.destroyAllWindows()
        
        
        # Log final cheating score
        print(f"\nFinal cheating score: {self.cheating_score}/100")
        print("Log saved to cheating_log.txt")
        
        # Get notification statistics if available
        if self.notification_system:
            try:
                notification_stats = self.notification_system.get_notification_stats()
                print(f"Notifications sent: {notification_stats.get('sent_notifications', 0)}")
            except Exception as e:
                print(f"Could not get notification stats: {e}")

if __name__ == "__main__":
    monitor = AdvancedExamMonitor()
    monitor.run()
