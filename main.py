"""
Advanced AI Exam Monitoring System
نظام مراقبة الامتحانات المتقدم بالذكاء الاصطناعي

Main entry point - uses optimized modular system
"""

from core.monitor import ExamMonitor

if __name__ == "__main__":
    monitor = ExamMonitor()
    monitor.run()
