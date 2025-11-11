"""
Alert Management System
نظام إدارة التنبيهات
"""

import time
from datetime import datetime
from collections import deque


class AlertManager:
    """Manages alerts and cheating score"""
    
    def __init__(self, config=None):
        """Initialize alert manager"""
        self.config = config
        self.cheating_score = 0
        self.alerts = []
        self.alert_history = deque(maxlen=10)
        self.last_alert_time = 0
        self.alert_cooldown = 5  # seconds
        
        # Load score penalties
        if config:
            self.SCORE_PENALTIES = config.get_score_penalties()
        else:
            self.SCORE_PENALTIES = {
                'multiple_people': 20,
                'face_away': 10,
                'forbidden_object': 25,
                'person_absent': 15,
                'talking': 20,
                'face_movement': 15,
                'suspicious_sounds': 15,
                'suspicious_emotion': 20
            }
        
        # Exam termination
        self.exam_termination_countdown = None
        self.exam_termination_start = None
        self.exam_termination_duration = 10
        self.exam_terminated = False
        
        # Metrics
        self.real_time_metrics = {
            'face_movements': 0,
            'audio_violations': 0,
            'object_violations': 0,
            'communication_attempts': 0,
            'suspicious_behavior': 0
        }
        
        # Incidents
        self.cheating_incidents = []
    
    def add_alert(self, message, alert_type, notification_system=None):
        """Add alert and update score"""
        current_time = time.time()
        
        # Cooldown check
        if current_time - self.last_alert_time < self.alert_cooldown:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert = f"[{timestamp}] {message}"
        
        if alert not in self.alert_history:
            self.alerts.append(alert)
            self.alert_history.append(alert)
            
            # Update score
            if alert_type in self.SCORE_PENALTIES:
                self.cheating_score = min(100, self.cheating_score + self.SCORE_PENALTIES[alert_type])
            
            # Check termination
            if self.cheating_score >= 100 and not self.exam_termination_countdown:
                self.start_exam_termination()
            
            # Update metrics
            self._update_metrics(alert_type)
            
            # Send notification
            if notification_system:
                priority = 'medium'
                if alert_type in ['forbidden_object', 'multiple_people']:
                    priority = 'high'
                elif alert_type == 'system_error':
                    priority = 'critical'
                
                notification_system.send_notification(
                    alert_type, message,
                    {'timestamp': timestamp, 'score': self.cheating_score},
                    priority
                )
            
            # Keep only recent alerts
            if len(self.alerts) > 5:
                self.alerts.pop(0)
            
            self.last_alert_time = current_time
            return True
        return False
    
    def add_object_alert(self, objects_detected, notification_system=None):
        """Add alert for detected objects"""
        for obj in objects_detected:
            message = f"Unauthorized object: {obj['name']} (Confidence: {obj['confidence']:.2f})"
            self.add_alert(message, "forbidden_object", notification_system)
            
            # Log incident
            incident = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'type': 'forbidden_object',
                'object': obj['name'],
                'confidence': obj['confidence'],
                'severity': obj['severity'],
                'position': obj['position']
            }
            self.cheating_incidents.append(incident)
    
    def _update_metrics(self, alert_type):
        """Update metrics based on alert type"""
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
    
    def update_exam_termination(self):
        """Update termination countdown"""
        if self.exam_termination_countdown and self.exam_termination_countdown > 0:
            elapsed = time.time() - self.exam_termination_start
            self.exam_termination_countdown = max(0, self.exam_termination_duration - elapsed)
            return self.exam_termination_countdown > 0
        return False
    
    def should_terminate(self):
        """Check if exam should be terminated"""
        return self.exam_termination_countdown is not None and self.exam_termination_countdown <= 0

