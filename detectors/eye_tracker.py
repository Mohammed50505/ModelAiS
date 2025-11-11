"""
Eye Gaze Tracking Module
وحدة تتبع النظرات
"""

import numpy as np
import time
from collections import deque


class EyeTracker:
    """Advanced eye gaze tracking for detecting screen focus"""
    
    def __init__(self, config=None):
        """Initialize eye tracker"""
        self.config = config
        
        # Eye tracking data
        self.eye_gaze_history = deque(maxlen=30)
        self.looking_away_count = 0
        self.looking_at_screen_count = 0
        self.last_gaze_direction = None
        
        # Thresholds
        self.LOOKING_AWAY_THRESHOLD = 3.0  # seconds
        self.GAZE_DEVIATION_THRESHOLD = 0.3  # normalized distance
        
        # Screen center (assumed)
        self.screen_center = (0.5, 0.4)  # Normalized coordinates
    
    def track_gaze(self, face_landmarks, frame_shape):
        """Track eye gaze direction"""
        if not face_landmarks:
            return None
        
        try:
            # Get eye landmarks (MediaPipe Face Mesh)
            # Left eye: 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
            # Right eye: 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398
            
            left_eye_landmarks = [
                33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246
            ]
            right_eye_landmarks = [
                362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398
            ]
            
            # Calculate eye centers
            left_eye_center = self._get_eye_center(face_landmarks, left_eye_landmarks, frame_shape)
            right_eye_center = self._get_eye_center(face_landmarks, right_eye_landmarks, frame_shape)
            
            if left_eye_center and right_eye_center:
                # Average eye center
                eye_center = (
                    (left_eye_center[0] + right_eye_center[0]) / 2,
                    (left_eye_center[1] + right_eye_center[1]) / 2
                )
                
                # Normalize coordinates
                normalized_center = (
                    eye_center[0] / frame_shape[1],
                    eye_center[1] / frame_shape[0]
                )
                
                self.eye_gaze_history.append(normalized_center)
                
                # Determine gaze direction relative to screen center
                gaze_direction = self._calculate_gaze_direction(normalized_center)
                
                return {
                    'center': normalized_center,
                    'direction': gaze_direction,
                    'looking_at_screen': self._is_looking_at_screen(normalized_center)
                }
        except Exception as e:
            print(f"Eye tracking error: {e}")
        
        return None
    
    def _get_eye_center(self, face_landmarks, eye_indices, frame_shape):
        """Calculate eye center from landmarks"""
        try:
            x_coords = [face_landmarks.landmark[i].x for i in eye_indices]
            y_coords = [face_landmarks.landmark[i].y for i in eye_indices]
            
            center_x = sum(x_coords) / len(x_coords) * frame_shape[1]
            center_y = sum(y_coords) / len(y_coords) * frame_shape[0]
            
            return (center_x, center_y)
        except:
            return None
    
    def _calculate_gaze_direction(self, eye_center):
        """Calculate gaze direction"""
        dx = eye_center[0] - self.screen_center[0]
        dy = eye_center[1] - self.screen_center[1]
        
        if abs(dx) > abs(dy):
            return "left" if dx < 0 else "right"
        else:
            return "up" if dy < 0 else "down"
    
    def _is_looking_at_screen(self, eye_center):
        """Check if looking at screen center"""
        distance = np.sqrt(
            (eye_center[0] - self.screen_center[0])**2 +
            (eye_center[1] - self.screen_center[1])**2
        )
        return distance < self.GAZE_DEVIATION_THRESHOLD
    
    def detect_prolonged_looking_away(self, gaze_data):
        """Detect if student is looking away for too long"""
        if not gaze_data:
            self.looking_away_count += 1
        elif not gaze_data.get('looking_at_screen', False):
            self.looking_away_count += 1
        else:
            self.looking_away_count = 0
            self.looking_at_screen_count += 1
        
        # Check threshold (assuming 30 FPS, 90 frames = 3 seconds)
        if self.looking_away_count > 90:  # 3 seconds at 30 FPS
            return True
        
        return False
