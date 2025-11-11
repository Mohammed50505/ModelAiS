"""
Hand Detection and Tracking Module
وحدة كشف وتتبع حركة اليدين
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque


class HandDetector:
    """Hand detection and suspicious hand movement tracking"""
    
    def __init__(self, config=None):
        """Initialize hand detector"""
        self.config = config
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize hands detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Hand movement tracking
        self.hand_positions_history = deque(maxlen=30)
        self.suspicious_hand_movements = 0
        self.hand_near_face_count = 0
        self.hand_near_phone_zone = 0
        
        # Thresholds
        self.SUSPICIOUS_MOVEMENT_THRESHOLD = 10  # movements
        self.HAND_NEAR_FACE_THRESHOLD = 0.15  # normalized distance
        self.PHONE_ZONE_THRESHOLD = 0.2  # normalized distance from bottom corners
    
    def process(self, frame):
        """Process frame and detect hands"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results
    
    def detect_suspicious_hand_movements(self, hand_results, face_landmarks=None):
        """Detect suspicious hand movements (typing on phone, writing)"""
        if not hand_results.multi_hand_landmarks:
            return False
        
        suspicious = False
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Get hand center (wrist)
            wrist = hand_landmarks.landmark[0]
            hand_center = (wrist.x, wrist.y)
            self.hand_positions_history.append(hand_center)
            
            # Check for rapid hand movements (typing pattern)
            if len(self.hand_positions_history) >= 10:
                movements = self._count_rapid_movements()
                if movements > self.SUSPICIOUS_MOVEMENT_THRESHOLD:
                    self.suspicious_hand_movements += 1
                    suspicious = True
            
            # Check if hand is near face (covering face or using phone)
            if face_landmarks:
                if self._is_hand_near_face(hand_landmarks, face_landmarks):
                    self.hand_near_face_count += 1
                    if self.hand_near_face_count > 5:
                        suspicious = True
            
            # Check if hand is in phone zone (bottom corners - typical phone position)
            if self._is_hand_in_phone_zone(hand_landmarks):
                self.hand_near_phone_zone += 1
                if self.hand_near_phone_zone > 3:
                    suspicious = True
        
        return suspicious
    
    def _count_rapid_movements(self):
        """Count rapid hand movements (indicates typing)"""
        if len(self.hand_positions_history) < 10:
            return 0
        
        movements = 0
        for i in range(1, len(self.hand_positions_history)):
            prev = self.hand_positions_history[i-1]
            curr = self.hand_positions_history[i]
            
            # Calculate distance
            dist = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
            if dist > 0.05:  # Significant movement
                movements += 1
        
        return movements
    
    def _is_hand_near_face(self, hand_landmarks, face_landmarks):
        """Check if hand is near face"""
        # Get hand center
        wrist = hand_landmarks.landmark[0]
        
        # Get face center (nose tip)
        try:
            nose_tip = face_landmarks.landmark[4]
            distance = np.sqrt(
                (wrist.x - nose_tip.x)**2 + 
                (wrist.y - nose_tip.y)**2
            )
            return distance < self.HAND_NEAR_FACE_THRESHOLD
        except:
            return False
    
    def _is_hand_in_phone_zone(self, hand_landmarks):
        """Check if hand is in typical phone position (bottom corners)"""
        wrist = hand_landmarks.landmark[0]
        
        # Phone zones: bottom-left and bottom-right corners
        bottom_left_zone = (wrist.x < self.PHONE_ZONE_THRESHOLD and 
                           wrist.y > (1 - self.PHONE_ZONE_THRESHOLD))
        bottom_right_zone = (wrist.x > (1 - self.PHONE_ZONE_THRESHOLD) and 
                            wrist.y > (1 - self.PHONE_ZONE_THRESHOLD))
        
        return bottom_left_zone or bottom_right_zone
    
    def detect_typing_pattern(self, hand_results):
        """Detect typing pattern (rapid finger movements)"""
        if not hand_results.multi_hand_landmarks:
            return False
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Get finger tips
            finger_tips = [
                hand_landmarks.landmark[4],   # Thumb
                hand_landmarks.landmark[8],   # Index
                hand_landmarks.landmark[12],  # Middle
                hand_landmarks.landmark[16],  # Ring
                hand_landmarks.landmark[20]   # Pinky
            ]
            
            # Check if multiple fingers are extended (typing position)
            extended_fingers = sum(1 for tip in finger_tips 
                                 if tip.y < hand_landmarks.landmark[0].y)
            
            if extended_fingers >= 3:
                return True
        
        return False
    
    def draw_hands(self, frame, hand_results):
        """Draw hand landmarks"""
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
        return frame
