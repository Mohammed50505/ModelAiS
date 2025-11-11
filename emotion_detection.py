"""
Advanced Emotion Detection Module
وحدة كشف المشاعر المتطورة
"""

import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import time
import json

class EmotionDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.emotion_history = deque(maxlen=30)
        self.current_emotion = 'neutral'
        self.emotion_confidence = 0.0
        
        self.suspicious_emotions = {
            'fear': 0.7,
            'surprise': 0.6,
            'angry': 0.5,
            'sad': 0.4
        }
        
        self.emotion_changes = []
        self.last_emotion_time = time.time()
    
    def detect_emotion(self, frame, face_landmarks=None):
        results = {
            'emotion': 'neutral',
            'confidence': 0.0,
            'suspicious': False,
            'suspicious_score': 0.0,
            'emotions': {},
            'features': {}
        }
        
        # Simple emotion detection based on facial features
        if face_landmarks:
            emotions = self.classify_emotion_from_landmarks(face_landmarks)
            results['emotions'] = emotions
            
            # Find dominant emotion
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                results['emotion'] = dominant_emotion[0]
                results['confidence'] = dominant_emotion[1]
        
        # Check for suspicious emotions
        suspicious_score = self.check_suspicious_emotions(results)
        results['suspicious'] = suspicious_score > 0.5
        results['suspicious_score'] = suspicious_score
        
        # Update history
        self.update_emotion_history(results)
        
        return results
    
    def classify_emotion_from_landmarks(self, face_landmarks):
        landmarks = face_landmarks.landmark
        
        # Calculate facial features
        eye_openness = self.calculate_eye_openness(landmarks)
        mouth_openness = self.calculate_mouth_openness(landmarks)
        brow_position = self.calculate_brow_position(landmarks)
        
        emotions = {}
        
        # Happy: high cheeks, wide mouth
        if mouth_openness > 0.02:
            emotions['happy'] = 0.8
        else:
            emotions['happy'] = 0.1
        
        # Sad: low brows, drooping mouth
        if brow_position > 0.6 and mouth_openness < 0.01:
            emotions['sad'] = 0.7
        else:
            emotions['sad'] = 0.1
        
        # Surprised: high brows, wide eyes
        if brow_position < 0.3 and eye_openness > 0.03:
            emotions['surprise'] = 0.8
        else:
            emotions['surprise'] = 0.1
        
        # Angry: low brows, tight mouth
        if brow_position < 0.4 and mouth_openness < 0.005:
            emotions['angry'] = 0.7
        else:
            emotions['angry'] = 0.1
        
        # Fear: high brows, wide eyes, open mouth
        if brow_position < 0.3 and eye_openness > 0.03 and mouth_openness > 0.015:
            emotions['fear'] = 0.8
        else:
            emotions['fear'] = 0.1
        
        # Neutral: balanced features
        emotions['neutral'] = 0.5
        
        # Normalize
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v/total for k, v in emotions.items()}
        
        return emotions
    
    def calculate_eye_openness(self, landmarks):
        left_eye_height = abs(landmarks[159].y - landmarks[145].y)
        right_eye_height = abs(landmarks[386].y - landmarks[374].y)
        return (left_eye_height + right_eye_height) / 2
    
    def calculate_mouth_openness(self, landmarks):
        return abs(landmarks[13].y - landmarks[14].y)
    
    def calculate_brow_position(self, landmarks):
        left_brow = landmarks[66].y
        right_brow = landmarks[296].y
        return (left_brow + right_brow) / 2
    
    def check_suspicious_emotions(self, results):
        suspicious_score = 0.0
        
        if 'emotions' in results and results['emotions']:
            for emotion, probability in results['emotions'].items():
                if emotion in self.suspicious_emotions:
                    threshold = self.suspicious_emotions[emotion]
                    if probability > threshold:
                        suspicious_score += (probability - threshold) * 2
        
        return min(suspicious_score, 1.0)
    
    def update_emotion_history(self, results):
        current_time = time.time()
        
        self.emotion_history.append({
            'time': current_time,
            'emotion': results['emotion'],
            'confidence': results['confidence'],
            'suspicious': results['suspicious'],
            'suspicious_score': results['suspicious_score']
        })
        
        if len(self.emotion_history) > 1:
            prev_emotion = self.emotion_history[-2]['emotion']
            if prev_emotion != results['emotion']:
                self.emotion_changes.append({
                    'time': current_time,
                    'from': prev_emotion,
                    'to': results['emotion'],
                    'duration': current_time - self.last_emotion_time
                })
        
        self.last_emotion_time = current_time
        self.current_emotion = results['emotion']
        self.emotion_confidence = results['confidence']
    
    def get_emotion_statistics(self):
        if not self.emotion_history:
            return {}
        
        stats = {
            'total_detections': len(self.emotion_history),
            'emotion_distribution': {},
            'suspicious_count': 0,
            'emotion_changes': len(self.emotion_changes),
            'current_emotion': self.current_emotion,
            'current_confidence': self.emotion_confidence
        }
        
        for entry in self.emotion_history:
            emotion = entry['emotion']
            stats['emotion_distribution'][emotion] = stats['emotion_distribution'].get(emotion, 0) + 1
            
            if entry['suspicious']:
                stats['suspicious_count'] += 1
        
        total = len(self.emotion_history)
        if total > 0:
            stats['emotion_distribution'] = {
                k: (v / total) * 100 for k, v in stats['emotion_distribution'].items()
            }
            stats['suspicious_percentage'] = (stats['suspicious_count'] / total) * 100
        
        return stats
    
    def get_emotion_alert(self):
        if not self.emotion_history:
            return None
        
        recent_suspicious = [
            entry for entry in list(self.emotion_history)[-10:]
            if entry['suspicious'] and entry['suspicious_score'] > 0.7
        ]
        
        if len(recent_suspicious) >= 3:
            return {
                'type': 'suspicious_emotion',
                'message': f"Suspicious emotional behavior detected: {len(recent_suspicious)} suspicious emotions",
                'severity': 'medium',
                'emotions': [entry['emotion'] for entry in recent_suspicious],
                'suspicious_score': sum(entry['suspicious_score'] for entry in recent_suspicious) / len(recent_suspicious)
            }
        
        return None
    
    def draw_emotion_overlay(self, frame, results):
        h, w = frame.shape[:2]
        
        # Draw emotion box
        cv2.rectangle(frame, (10, 10), (300, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 120), (255, 255, 255), 2)
        
        # Draw emotion text
        emotion_text = f"Emotion: {results['emotion'].upper()}"
        confidence_text = f"Confidence: {results['confidence']:.2f}"
        suspicious_text = f"Suspicious: {'YES' if results['suspicious'] else 'NO'}"
        
        cv2.putText(frame, emotion_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, confidence_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        suspicious_color = (0, 0, 255) if results['suspicious'] else (0, 255, 0)
        cv2.putText(frame, suspicious_text, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, suspicious_color, 2)
        
        # Draw emotion bars
        if 'emotions' in results and results['emotions']:
            bar_y = 130
            for i, (emotion, prob) in enumerate(list(results['emotions'].items())[:5]):
                bar_width = int(prob * 200)
                
                if emotion in self.suspicious_emotions:
                    color = (0, 0, 255)
                elif emotion == 'happy':
                    color = (0, 255, 0)
                else:
                    color = (255, 255, 255)
                
                cv2.rectangle(frame, (10, bar_y + i * 20), (10 + bar_width, bar_y + i * 20 + 15), color, -1)
                cv2.putText(frame, f"{emotion}: {prob:.2f}", (220, bar_y + i * 20 + 12), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame

if __name__ == "__main__":
    detector = EmotionDetector()
    print("✅ Emotion detector initialized successfully!")
