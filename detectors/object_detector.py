"""
Object Detection Module using YOLO
وحدة كشف الأجسام باستخدام YOLO
"""

import cv2
import numpy as np
import time
from ultralytics import YOLO


class ObjectDetector:
    """Fast object detection using YOLO with optimizations"""
    
    def __init__(self, config=None):
        """Initialize YOLO detector with optimizations"""
        self.config = config
        
        # Load model
        model_path = config.YOLO_MODEL_PATH if config else 'yolov8n.pt'
        print(f"📦 Loading YOLO model: {model_path}")
        self.yolo_model = YOLO(model_path)
        
        # Detect device (GPU/CPU)
        try:
            import torch
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            if self.device == 'cuda':
                print(f"🚀 GPU detected: {torch.cuda.get_device_name(0)}")
            else:
                print("💻 Using CPU for inference")
        except ImportError:
            self.device = 'cpu'
            print("💻 Using CPU for inference")
        
        # Optimize model
        if hasattr(self.yolo_model, 'fuse'):
            self.yolo_model.fuse()
        
        # Load forbidden objects
        if config:
            self.forbidden_objects = config.get_forbidden_objects()
        else:
            self.forbidden_objects = [
                'cell phone', 'smartphone', 'mobile phone', 'phone',
                'laptop', 'computer', 'tablet', 'ipad', 'notebook',
                'headphone', 'earphone', 'airpods', 'earbuds',
                'smartwatch', 'watch', 'calculator', 'book', 'paper'
            ]
        
        print("✅ YOLO model loaded and optimized")
        
        # Frame skipping for speed (process every N frames)
        # Adaptive: use more skipping on CPU, less on GPU
        self.frame_skip = 3 if self.device == 'cpu' else 2
        self.frame_count = 0
        self.last_results = None
        
        # Cache for faster processing
        self.result_cache = {}
        self.cache_timeout = 0.1  # 100ms cache
        self.last_cache_time = 0
    
    def detect(self, frame):
        """Detect forbidden objects in frame (with frame skipping and caching for speed)"""
        self.frame_count += 1
        current_time = time.time()
        
        # Skip frames for speed (only process every N frames)
        if self.frame_count % self.frame_skip != 0:
            # Use cached results if available and fresh
            if (self.last_results and 
                current_time - self.last_cache_time < self.cache_timeout):
                return self.last_results
            return []
        
        try:
            conf_threshold = self.config.YOLO_CONFIDENCE_THRESHOLD if self.config else 0.5
            
            # Run YOLO with optimized settings
            # Use smaller image size for CPU, larger for GPU
            img_size = 480 if self.device == 'cpu' else 640
            
            results = self.yolo_model(
                frame,
                verbose=False,
                conf=conf_threshold,
                imgsz=img_size,
                half=False,
                device=self.device,
                max_det=20  # Limit detections for speed
            )
            
            objects_detected = []
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy().astype(int)
                    
                    for box, conf, cls in zip(boxes, confidences, classes):
                        class_name = result.names[cls]
                        
                        if class_name in self.forbidden_objects and conf > conf_threshold:
                            x1, y1, x2, y2 = map(int, box)
                            
                            objects_detected.append({
                                'name': class_name,
                                'confidence': float(conf),
                                'position': (x1, y1, x2, y2),
                                'severity': 'high' if class_name in ['cell phone', 'smartphone', 'laptop'] else 'medium'
                            })
            
            self.last_results = objects_detected
            self.last_cache_time = current_time
            return objects_detected
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []
    
    def draw_detections(self, frame, objects_detected):
        """Draw bounding boxes on frame"""
        for obj in objects_detected:
            x1, y1, x2, y2 = obj['position']
            
            # Color based on severity
            if obj['severity'] == 'high':
                color = (0, 0, 255)  # Red
            elif obj['name'] in ['book', 'notebook', 'paper']:
                color = (0, 165, 255)  # Orange
            else:
                color = (0, 255, 255)  # Yellow
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame, f"{obj['name']} {obj['confidence']:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
        
        return frame

