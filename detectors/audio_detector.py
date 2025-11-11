"""
Audio Detection Module
وحدة كشف الصوت
"""

import numpy as np
import speech_recognition as sr
import threading
import time


class AudioDetector:
    """Audio monitoring and sound pattern detection"""
    
    def __init__(self, config=None):
        """Initialize audio detector"""
        self.config = config
        self.audio_recognizer = sr.Recognizer()
        self.audio_monitoring = False
        self.audio_thread = None
        
        self.sound_patterns = {
            'whispering': 0,
            'talking': 0,
            'keyboard_typing': 0,
            'paper_rustling': 0,
            'phone_vibration': 0,
            'other_sounds': 0
        }
        
        self.talking_start = None
        self.TALKING_THRESHOLD = 2.0
        
        if config:
            thresholds = config.get_time_thresholds()
            self.TALKING_THRESHOLD = thresholds.get('talking', 2.0)
    
    def start_monitoring(self, alert_callback=None):
        """Start audio monitoring in separate thread"""
        self.audio_monitoring = True
        self.alert_callback = alert_callback
        self.audio_thread = threading.Thread(target=self._monitor_audio, daemon=True)
        self.audio_thread.start()
    
    def stop_monitoring(self):
        """Stop audio monitoring"""
        self.audio_monitoring = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
    
    def _monitor_audio(self):
        """Audio monitoring loop"""
        try:
            with sr.Microphone() as source:
                self.audio_recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.audio_monitoring:
                    try:
                        audio = self.audio_recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                        
                        # Analyze sound patterns
                        self._analyze_sound_patterns(audio_data)
                        
                        # Try speech recognition
                        try:
                            text = self.audio_recognizer.recognize_google(audio)
                            if text.strip():
                                self._detect_talking()
                        except sr.UnknownValueError:
                            pass
                        except Exception:
                            pass
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception:
                        continue
        except Exception as e:
            print(f"Audio monitoring error: {e}")
    
    def _analyze_sound_patterns(self, audio_data):
        """Analyze audio for sound patterns"""
        if len(audio_data) == 0:
            return
        
        rms = np.sqrt(np.mean(audio_data**2))
        zero_crossings = np.sum(np.diff(np.sign(audio_data)))
        
        if rms > 1000:  # High amplitude
            if zero_crossings > 1000:  # High frequency
                self.sound_patterns['keyboard_typing'] += 1
                if self.sound_patterns['keyboard_typing'] > 5 and self.alert_callback:
                    self.alert_callback("Suspicious keyboard activity detected", "suspicious_sounds")
                    self.sound_patterns['keyboard_typing'] = 0
            else:  # Low frequency
                self.sound_patterns['talking'] += 1
                if self.sound_patterns['talking'] > 3 and self.alert_callback:
                    self.alert_callback("Suspicious talking detected", "talking")
                    self.sound_patterns['talking'] = 0
        elif rms > 500:  # Medium amplitude
            if zero_crossings < 100:  # Low frequency
                self.sound_patterns['whispering'] += 1
                if self.sound_patterns['whispering'] > 5 and self.alert_callback:
                    self.alert_callback("Whispering detected", "suspicious_sounds")
                    self.sound_patterns['whispering'] = 0
            else:
                self.sound_patterns['paper_rustling'] += 1
                if self.sound_patterns['paper_rustling'] > 8 and self.alert_callback:
                    self.alert_callback("Paper rustling detected", "suspicious_sounds")
                    self.sound_patterns['paper_rustling'] = 0
    
    def _detect_talking(self):
        """Detect suspicious talking"""
        current_time = time.time()
        
        if self.talking_start is None:
            self.talking_start = current_time
        elif current_time - self.talking_start > self.TALKING_THRESHOLD:
            if self.alert_callback:
                self.alert_callback("Suspicious talking detected", "talking")
            self.talking_start = None

