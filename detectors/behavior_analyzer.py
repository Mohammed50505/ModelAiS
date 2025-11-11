"""
Advanced Behavior Analysis Module
وحدة التحليل السلوكي المتقدم
"""

import time
import numpy as np
from collections import deque
from datetime import datetime


class BehaviorAnalyzer:
    """Advanced behavioral pattern analysis for cheating detection"""
    
    def __init__(self, config=None):
        """Initialize behavior analyzer"""
        self.config = config
        
        # Behavior patterns
        self.behavior_patterns = {
            'frequent_looking_away': deque(maxlen=100),
            'rapid_head_movements': deque(maxlen=50),
            'hand_to_face_patterns': deque(maxlen=50),
            'posture_changes': deque(maxlen=50),
            'object_detections': deque(maxlen=50)
        }
        
        # Risk scoring
        self.risk_score = 0
        self.risk_history = deque(maxlen=100)
        
        # Time windows
        self.SHORT_WINDOW = 10  # seconds
        self.MEDIUM_WINDOW = 30  # seconds
        self.LONG_WINDOW = 60  # seconds
        
        # Risk thresholds
        self.HIGH_RISK_THRESHOLD = 70
        self.MEDIUM_RISK_THRESHOLD = 40
        self.LOW_RISK_THRESHOLD = 20
    
    def analyze_pattern(self, detection_data):
        """Analyze detection patterns and calculate risk"""
        current_time = time.time()
        
        # Record patterns
        if detection_data.get('looking_away'):
            self.behavior_patterns['frequent_looking_away'].append(current_time)
        
        if detection_data.get('rapid_movement'):
            self.behavior_patterns['rapid_head_movements'].append(current_time)
        
        if detection_data.get('hand_near_face'):
            self.behavior_patterns['hand_to_face_patterns'].append(current_time)
        
        if detection_data.get('posture_change'):
            self.behavior_patterns['posture_changes'].append(current_time)
        
        if detection_data.get('object_detected'):
            self.behavior_patterns['object_detections'].append(current_time)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(current_time)
        self.risk_score = risk_score
        self.risk_history.append({
            'timestamp': current_time,
            'score': risk_score,
            'level': self._get_risk_level(risk_score)
        })
        
        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'patterns': self._identify_patterns(current_time)
        }
    
    def _calculate_risk_score(self, current_time):
        """Calculate overall risk score"""
        score = 0
        
        # Frequent looking away (high weight)
        recent_look_aways = [t for t in self.behavior_patterns['frequent_looking_away'] 
                           if current_time - t < self.SHORT_WINDOW]
        score += min(len(recent_look_aways) * 5, 30)
        
        # Rapid movements (medium weight)
        recent_movements = [t for t in self.behavior_patterns['rapid_head_movements'] 
                          if current_time - t < self.SHORT_WINDOW]
        score += min(len(recent_movements) * 3, 20)
        
        # Hand to face (high weight - using phone)
        recent_hand_face = [t for t in self.behavior_patterns['hand_to_face_patterns'] 
                          if current_time - t < self.SHORT_WINDOW]
        score += min(len(recent_hand_face) * 4, 25)
        
        # Posture changes (medium weight)
        recent_posture = [t for t in self.behavior_patterns['posture_changes'] 
                        if current_time - t < self.MEDIUM_WINDOW]
        score += min(len(recent_posture) * 2, 15)
        
        # Object detections (very high weight)
        recent_objects = [t for t in self.behavior_patterns['object_detections'] 
                        if current_time - t < self.SHORT_WINDOW]
        score += min(len(recent_objects) * 10, 40)
        
        return min(score, 100)
    
    def _get_risk_level(self, score):
        """Get risk level from score"""
        if score >= self.HIGH_RISK_THRESHOLD:
            return 'high'
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            return 'medium'
        elif score >= self.LOW_RISK_THRESHOLD:
            return 'low'
        return 'normal'
    
    def _identify_patterns(self, current_time):
        """Identify suspicious behavioral patterns"""
        patterns = []
        
        # Pattern 1: Frequent looking away
        look_aways = [t for t in self.behavior_patterns['frequent_looking_away'] 
                     if current_time - t < self.SHORT_WINDOW]
        if len(look_aways) > 5:
            patterns.append('frequent_looking_away')
        
        # Pattern 2: Rapid movements (nervous behavior)
        movements = [t for t in self.behavior_patterns['rapid_head_movements'] 
                   if current_time - t < self.SHORT_WINDOW]
        if len(movements) > 8:
            patterns.append('nervous_behavior')
        
        # Pattern 3: Hand to face repeatedly (using phone)
        hand_face = [t for t in self.behavior_patterns['hand_to_face_patterns'] 
                   if current_time - t < self.SHORT_WINDOW]
        if len(hand_face) > 3:
            patterns.append('phone_usage_suspected')
        
        # Pattern 4: Multiple objects detected
        objects = [t for t in self.behavior_patterns['object_detections'] 
                 if current_time - t < self.SHORT_WINDOW]
        if len(objects) > 2:
            patterns.append('multiple_forbidden_objects')
        
        return patterns
    
    def get_risk_summary(self):
        """Get risk summary for reporting"""
        if not self.risk_history:
            return None
        
        recent_risks = [r for r in self.risk_history if time.time() - r['timestamp'] < 60]
        
        if not recent_risks:
            return None
        
        avg_risk = np.mean([r['score'] for r in recent_risks])
        max_risk = max([r['score'] for r in recent_risks])
        
        return {
            'current_risk': self.risk_score,
            'average_risk': avg_risk,
            'peak_risk': max_risk,
            'risk_level': self._get_risk_level(avg_risk),
            'trend': self._calculate_trend()
        }
    
    def _calculate_trend(self):
        """Calculate risk trend (increasing/decreasing)"""
        if len(self.risk_history) < 10:
            return 'stable'
        
        recent = [r['score'] for r in list(self.risk_history)[-10:]]
        older = [r['score'] for r in list(self.risk_history)[-20:-10]]
        
        if not older:
            return 'stable'
        
        recent_avg = np.mean(recent)
        older_avg = np.mean(older)
        
        if recent_avg > older_avg * 1.2:
            return 'increasing'
        elif recent_avg < older_avg * 0.8:
            return 'decreasing'
        return 'stable'
