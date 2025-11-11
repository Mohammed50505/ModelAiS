"""
Detectors module
وحدة الكواشف
"""

from .face_detector import FaceDetector
from .object_detector import ObjectDetector
from .audio_detector import AudioDetector

__all__ = ['FaceDetector', 'ObjectDetector', 'AudioDetector']

