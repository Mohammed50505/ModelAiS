#!/usr/bin/env python3
"""
نظام تجميد الشاشة - Screen Lock System
Advanced AI Exam Monitoring System - Anti-Cheating Screen Lock
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading
import json
import os
from datetime import datetime

class ScreenLock:
    def __init__(self):
        self.root = None
        self.is_locked = False
        self.lock_start_time = None
        self.student_info = {}
        
    def create_lock_screen(self, student_name, exam_title):
        """Create full-screen lock overlay"""
        try:
            # Create main window
            self.root = tk.Tk()
            self.root.title("EXAM IN PROGRESS - DO NOT CLOSE")
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Configure window
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.attributes('-disabled', True)
            
            # Prevent closing
            self.root.protocol("WM_DELETE_WINDOW", self.prevent_close)
            self.root.bind("<Key>", self.prevent_keys)
            self.root.bind("<Button>", self.prevent_mouse)
            
            # Create main frame
            main_frame = tk.Frame(self.root, bg='#1a1a1a')
            main_frame.pack(fill='both', expand=True)
            
            # Header
            header_frame = tk.Frame(main_frame, bg='#2c3e50', height=100)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            title_label = tk.Label(
                header_frame, 
                text="🚨 EXAM IN PROGRESS - DO NOT CLOSE 🚨",
                font=('Arial', 24, 'bold'),
                fg='white',
                bg='#2c3e50'
            )
            title_label.pack(pady=30)
            
            # Student info frame
            info_frame = tk.Frame(main_frame, bg='#34495e', padx=50, pady=30)
            info_frame.pack(fill='x')
            
            student_label = tk.Label(
                info_frame,
                text=f"Student: {student_name}",
                font=('Arial', 18),
                fg='white',
                bg='#34495e'
            )
            student_label.pack()
            
            exam_label = tk.Label(
                info_frame,
                text=f"Exam: {exam_title}",
                font=('Arial', 16),
                fg='#ecf0f1',
                bg='#34495e'
            )
            exam_label.pack(pady=10)
            
            # Warning frame
            warning_frame = tk.Frame(main_frame, bg='#e74c3c', padx=50, pady=30)
            warning_frame.pack(fill='x')
            
            warning_label = tk.Label(
                warning_frame,
                text="⚠️ WARNING: Screen is locked for exam integrity ⚠️",
                font=('Arial', 20, 'bold'),
                fg='white',
                bg='#e74c3c'
            )
            warning_label.pack()
            
            warning_text = tk.Label(
                warning_frame,
                text="• Do not attempt to close this window\n• Do not use Alt+Tab or other shortcuts\n• Camera is monitoring your activities\n• Any suspicious behavior will be recorded",
                font=('Arial', 14),
                fg='white',
                bg='#e74c3c',
                justify='left'
            )
            warning_text.pack(pady=20)
            
            # Timer frame
            timer_frame = tk.Frame(main_frame, bg='#27ae60', padx=50, pady=30)
            timer_frame.pack(fill='x')
            
            self.timer_label = tk.Label(
                timer_frame,
                text="Time Elapsed: 00:00:00",
                font=('Arial', 18, 'bold'),
                fg='white',
                bg='#27ae60'
            )
            self.timer_label.pack()
            
            # Instructions frame
            instructions_frame = tk.Frame(main_frame, bg='#3498db', padx=50, pady=30)
            instructions_frame.pack(fill='x')
            
            instructions_label = tk.Label(
                instructions_frame,
                text="📋 EXAM INSTRUCTIONS:",
                font=('Arial', 18, 'bold'),
                fg='white',
                bg='#3498db'
            )
            instructions_label.pack()
            
            instructions_text = tk.Label(
                instructions_frame,
                text="• Answer all questions in the exam interface\n• Do not switch windows or applications\n• Stay focused on the exam\n• Submit when finished",
                font=('Arial', 14),
                fg='white',
                bg='#3498db',
                justify='left'
            )
            instructions_text.pack(pady=20)
            
            # Footer
            footer_frame = tk.Frame(main_frame, bg='#2c3e50', height=80)
            footer_frame.pack(fill='x', side='bottom')
            footer_frame.pack_propagate(False)
            
            footer_label = tk.Label(
                footer_frame,
                text="Advanced AI Exam Monitoring System v2.0 | Screen Lock Active",
                font=('Arial', 12),
                fg='#bdc3c7',
                bg='#2c3e50'
            )
            footer_label.pack(pady=30)
            
            # Start timer
            self.lock_start_time = time.time()
            self.update_timer()
            
            # Store student info
            self.student_info = {
                'name': student_name,
                'exam': exam_title,
                'start_time': datetime.now().isoformat()
            }
            
            self.is_locked = True
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_lock_status, daemon=True)
            self.monitor_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error creating lock screen: {e}")
            return False
    
    def update_timer(self):
        """Update elapsed time display"""
        if self.is_locked and self.lock_start_time:
            elapsed = time.time() - self.lock_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            time_str = f"Time Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}"
            
            if self.timer_label:
                self.timer_label.config(text=time_str)
            
            # Update every second
            if self.is_locked:
                self.root.after(1000, self.update_timer)
    
    def monitor_lock_status(self):
        """Monitor if lock should be released"""
        while self.is_locked:
            try:
                # Check for unlock command
                if os.path.exists('unlock_screen.json'):
                    with open('unlock_screen.json', 'r') as f:
                        unlock_data = json.load(f)
                    
                    if unlock_data.get('unlock', False):
                        self.unlock_screen()
                        break
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error monitoring lock status: {e}")
                time.sleep(1)
    
    def unlock_screen(self):
        """Unlock the screen"""
        try:
            self.is_locked = False
            
            # Save lock session data
            lock_session = {
                'student_name': self.student_info.get('name'),
                'exam_title': self.student_info.get('exam'),
                'start_time': self.student_info.get('start_time'),
                'end_time': datetime.now().isoformat(),
                'duration': time.time() - self.lock_start_time if self.lock_start_time else 0
            }
            
            # Save to file
            if os.path.exists('screen_lock_sessions.json'):
                with open('screen_lock_sessions.json', 'r') as f:
                    sessions = json.load(f)
            else:
                sessions = []
            
            sessions.append(lock_session)
            
            with open('screen_lock_sessions.json', 'w') as f:
                json.dump(sessions, f, indent=2)
            
            # Close window
            if self.root:
                self.root.destroy()
                self.root = None
            
            # Remove unlock command
            if os.path.exists('unlock_screen.json'):
                os.remove('unlock_screen.json')
            
            print("✅ Screen unlocked successfully")
            
        except Exception as e:
            print(f"Error unlocking screen: {e}")
    
    def prevent_close(self):
        """Prevent window from being closed"""
        messagebox.showwarning(
            "Access Denied",
            "This window cannot be closed during the exam.\nPlease contact your instructor if you need assistance."
        )
    
    def prevent_keys(self, event):
        """Prevent keyboard shortcuts"""
        # Allow only specific keys
        allowed_keys = ['Tab', 'Return', 'BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down']
        
        if event.keysym not in allowed_keys:
            return "break"
    
    def prevent_mouse(self, event):
        """Prevent mouse clicks outside allowed areas"""
        # Allow clicks on the main window
        if event.widget == self.root:
            return
        else:
            return "break"

def main():
    """Main function for testing"""
    print("🔒 Screen Lock System")
    print("This module provides screen locking functionality for exams")
    print("It should be imported and used by the main monitoring system")

if __name__ == "__main__":
    main()
