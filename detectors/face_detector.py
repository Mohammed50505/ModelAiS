"""
Face Detection Module
وحدة كشف الوجه
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class FaceDetector:
    """Face detection and tracking using MediaPipe"""
    
    def __init__(self, config=None):
        """Initialize face detector"""
        self.config = config
        
        # Initialize MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Get confidence thresholds
        face_conf = config.MEDIAPIPE_FACE_DETECTION_CONFIDENCE if config else 0.5
        mesh_conf = config.MEDIAPIPE_FACE_MESH_CONFIDENCE if config else 0.5
        pose_conf = config.MEDIAPIPE_POSE_CONFIDENCE if config else 0.5
        
        # Initialize detectors
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=face_conf
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=mesh_conf,
            min_tracking_confidence=mesh_conf
        )
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=pose_conf,
            min_tracking_confidence=pose_conf
        )
        
        # Face movement tracking
        self.face_movement_start = None
        self.face_movement_direction = None
        self.face_movement_threshold = 3.0
        self.face_center_history = deque(maxlen=30)
        self.face_movement_sensitivity = 50
        
        # State tracking
        self.last_face_time = time.time()
        self.face_away_start = None
        self.person_absent_start = None
        self.last_person_time = time.time()
        
        # Thresholds
        if config:
            thresholds = config.get_time_thresholds()
            self.FACE_AWAY_THRESHOLD = thresholds.get('face_away', 5.0)
            self.PERSON_ABSENT_THRESHOLD = thresholds.get('person_absent', 3.0)
        else:
            self.FACE_AWAY_THRESHOLD = 5.0
            self.PERSON_ABSENT_THRESHOLD = 3.0
    
    def process(self, frame):
        """Process frame and return detection results"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe (optimized for speed)
        face_results = self.face_detection.process(rgb_frame)
        face_mesh_results = self.face_mesh.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        
        return {
            'face': face_results,
            'face_mesh': face_mesh_results,
            'pose': pose_results
        }
    
    def detect_face_away(self, face_results):
        """Detect if student is looking away"""
        current_time = time.time()
        
        if face_results.detections:
            self.last_face_time = current_time
            if self.face_away_start:
                self.face_away_start = None
            return False
        else:
            if self.face_away_start is None:
                self.face_away_start = current_time
            elif current_time - self.face_away_start > self.FACE_AWAY_THRESHOLD:
                self.face_away_start = None
                return True
        return False
    
    def detect_person_absence(self, pose_results):
        """Detect if student is not present"""
        current_time = time.time()
        
        if pose_results.pose_landmarks:
            self.last_person_time = current_time
            if self.person_absent_start:
                self.person_absent_start = None
            return False
        else:
            if self.person_absent_start is None:
                self.person_absent_start = current_time
            elif current_time - self.person_absent_start > self.PERSON_ABSENT_THRESHOLD:
                self.person_absent_start = None
                return True
        return False
    
    def detect_multiple_people(self, pose_results):
        """Detect if multiple people are in frame"""
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            visible_landmarks = sum(1 for lm in landmarks if lm.visibility > 0.5)
            return visible_landmarks > 33
        return False
    
    def detect_face_movement(self, face_landmarks, frame):
        """Detect face movement direction"""
        if not face_landmarks:
            return None
        
        try:
            nose_tip = face_landmarks.landmark[4]
            face_center = (int(nose_tip.x * frame.shape[1]), int(nose_tip.y * frame.shape[0]))
            self.face_center_history.append(face_center)
            
            if len(self.face_center_history) < 10:
                return None
            
            start_point = self.face_center_history[0]
            end_point = self.face_center_history[-1]
            
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            
            direction = None
            if abs(dx) > self.face_movement_sensitivity:
                direction = "right" if dx > 0 else "left"
            elif abs(dy) > self.face_movement_sensitivity:
                direction = "down" if dy > 0 else "up"
            
            if direction:
                if self.face_movement_direction != direction:
                    self.face_movement_direction = direction
                    self.face_movement_start = time.time()
                elif self.face_movement_start and time.time() - self.face_movement_start > self.face_movement_threshold:
                    self.face_movement_start = None
                    return direction
            
            return None
        except Exception:
            return None
    
    def draw_landmarks(self, frame, face_mesh_results, pose_results):
        """Draw landmarks on frame"""
        # Draw face mesh
        if face_mesh_results.multi_face_landmarks:
            for face_landmarks in face_mesh_results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1)
                )
        
        # Draw pose
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )
        
        return frame

