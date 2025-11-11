"""
Posture Detection Module
وحدة كشف وضعية الجلوس
"""

import numpy as np
import time
from collections import deque


class PostureDetector:
    """Detect suspicious postures and body positions"""
    
    def __init__(self, config=None):
        """Initialize posture detector"""
        self.config = config
        
        # Posture tracking
        self.posture_history = deque(maxlen=30)
        self.suspicious_posture_count = 0
        
        # Thresholds
        self.SUSPICIOUS_POSTURE_THRESHOLD = 5  # consecutive frames
        self.LEANING_THRESHOLD = 0.15  # normalized distance
        self.SLOUCHING_THRESHOLD = 0.2  # normalized distance
    
    def detect_posture(self, pose_landmarks, frame_shape):
        """Detect body posture"""
        if not pose_landmarks:
            return None
        
        try:
            landmarks = pose_landmarks.landmark
            
            # Key points for posture detection
            nose = landmarks[0] if len(landmarks) > 0 else None
            left_shoulder = landmarks[11] if len(landmarks) > 11 else None
            right_shoulder = landmarks[12] if len(landmarks) > 12 else None
            left_hip = landmarks[23] if len(landmarks) > 23 else None
            right_hip = landmarks[24] if len(landmarks) > 24 else None
            
            if not all([nose, left_shoulder, right_shoulder, left_hip, right_hip]):
                return None
            
            # Calculate posture metrics
            posture_data = {
                'leaning_left': self._is_leaning_left(left_shoulder, right_shoulder, nose),
                'leaning_right': self._is_leaning_right(left_shoulder, right_shoulder, nose),
                'slouching': self._is_slouching(left_shoulder, left_hip, right_shoulder, right_hip),
                'turned_away': self._is_turned_away(left_shoulder, right_shoulder, nose),
                'too_close': self._is_too_close_to_screen(nose, frame_shape),
                'too_far': self._is_too_far_from_screen(nose, frame_shape)
            }
            
            self.posture_history.append(posture_data)
            
            # Check for suspicious patterns
            is_suspicious = self._check_suspicious_posture(posture_data)
            
            return {
                **posture_data,
                'suspicious': is_suspicious
            }
        except Exception as e:
            print(f"Posture detection error: {e}")
            return None
    
    def _is_leaning_left(self, left_shoulder, right_shoulder, nose):
        """Check if leaning left (looking at phone/paper on left)"""
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        deviation = nose.x - shoulder_center_x
        return deviation < -self.LEANING_THRESHOLD
    
    def _is_leaning_right(self, left_shoulder, right_shoulder, nose):
        """Check if leaning right (looking at phone/paper on right)"""
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        deviation = nose.x - shoulder_center_x
        return deviation > self.LEANING_THRESHOLD
    
    def _is_slouching(self, left_shoulder, left_hip, right_shoulder, right_hip):
        """Check if slouching (hiding something)"""
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_center_y = (left_hip.y + right_hip.y) / 2
        torso_length = abs(shoulder_center_y - hip_center_y)
        
        # Slouching: shoulders too low relative to hips
        return (shoulder_center_y - hip_center_y) > self.SLOUCHING_THRESHOLD
    
    def _is_turned_away(self, left_shoulder, right_shoulder, nose):
        """Check if body is turned away from screen"""
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        # If nose is significantly off-center from shoulders
        deviation = abs(nose.x - shoulder_center_x)
        return deviation > 0.25
    
    def _is_too_close_to_screen(self, nose, frame_shape):
        """Check if too close to screen (hiding something)"""
        # Normalized distance from center
        center_x = 0.5
        center_y = 0.4
        distance = np.sqrt((nose.x - center_x)**2 + (nose.y - center_y)**2)
        return distance < 0.15  # Very close
    
    def _is_too_far_from_screen(self, nose, frame_shape):
        """Check if too far from screen (not engaged)"""
        center_x = 0.5
        center_y = 0.4
        distance = np.sqrt((nose.x - center_x)**2 + (nose.y - center_y)**2)
        return distance > 0.4  # Very far
    
    def _check_suspicious_posture(self, posture_data):
        """Check if posture is suspicious"""
        suspicious_indicators = [
            posture_data['leaning_left'],
            posture_data['leaning_right'],
            posture_data['slouching'],
            posture_data['turned_away']
        ]
        
        if sum(suspicious_indicators) >= 2:  # Multiple indicators
            self.suspicious_posture_count += 1
            if self.suspicious_posture_count >= self.SUSPICIOUS_POSTURE_THRESHOLD:
                return True
        else:
            self.suspicious_posture_count = 0
        
        return False
