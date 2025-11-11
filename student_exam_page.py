#!/usr/bin/env python3
"""
Student Exam Page - Final Version with Immersive Lock
Advanced AI Exam Monitoring System - Student Interface
This file handles student login, exam display, and submission, with an immersive
exam experience (simulated screen lock) and automatic model activation.
"""

import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
import cv2 # Keep for potential camera integration/mocking
import numpy as np # Keep for potential camera integration/mocking
import logging
import sys

# Configure logging for better debugging (these logs will go to terminal, not Streamlit UI)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure UTF-8 encoding for standard output
sys.stdout.reconfigure(encoding='utf-8')

# Configure Streamlit page settings
st.set_page_config(
    page_title="صفحة امتحان الطالب",
    page_icon="👨‍🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI/UX (consistent with admin dashboard)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="st-emotion-cache"] {
        font-family: 'Inter', sans-serif;
        color: #333333;
        background-color: #f0f2f6;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
        font-weight: 600;
    }

    /* Hide sidebar during active exam for "screen freeze" effect */
    .st-emotion-cache-vk33gh { /* Target the sidebar container */
        display: var(--sidebar-display, block); /* Default to block, can be set to none */
        background-color: #ffffff;
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-right: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .reportview-container .main .block-container{
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .st-emotion-cache-use3lb { /* Primary button */
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
        border: none;
    }
    .st-emotion-cache-use3lb:hover {
        background-color: #2980b9;
        color: white;
    }

    .st-emotion-cache-v0u5xx { /* Secondary button */
        background-color: #ecf0f1;
        color: #34495e;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
        border: 1px solid #bdc3c7;
    }
    .st-emotion-cache-v0u5xx:hover {
        background-color: #dde1e5;
        color: #34495e;
    }
    
    .st-emotion-cache-zq5aqz { /* Input field label */
        color: #34495e;
        font-weight: 500;
    }
    .st-emotion-cache-1h6d2gq { /* Input field container */
        border-radius: 8px;
        border: 1px solid #bdc3c7;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        padding: 0.5rem;
    }
    .st-emotion-cache-1h6d2gq input, .st-emotion-cache-1h6d2gq textarea {
        border: none !important;
        background: none !important;
        box-shadow: none !important;
    }

    .exam-card {
        background-color: #ffffff;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border-left: 5px solid #2ecc71; /* Green accent for success/info */
    }
    .exam-card h5 {
        color: #2ecc71;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .exam-card p {
        font-size: 0.9rem;
        color: #555;
        line-height: 1.4;
    }

    .main-header {
        background-color: #ffffff;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h2 {
        color: #3498db;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.1rem;
        color: #555;
    }

    /* Question Card */
    .question-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-left: 4px solid #3498db; /* Blue accent */
    }
    .question-card h4 {
        color: #3498db;
        margin-bottom: 0.8rem;
    }
    .question-card p {
        color: #333;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Camera Warning Styling */
    .camera-warning {
        background-color: #fff3cd; /* Light yellow */
        color: #856404; /* Dark yellow text */
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7; /* Yellow border */
        margin: 1rem 0;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .camera-warning.active {
        background-color: #d4edda; /* Light green for active camera */
        color: #155724; /* Dark green text */
        border: 1px solid #c3e6cb;
    }
    .camera-placeholder img {
        border-radius: 8px;
        border: 2px dashed #95a5a6;
        margin-top: 1rem;
    }

    /* General Streamlit alerts for consistency */
    .st-emotion-cache-1c8882q { /* Info alert */
        background-color: #e8f5e9; /* Light green */
        color: #388e3c;
        border-left: 5px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-1c8882q p { /* Text inside info alert */
        color: #388e3c;
    }

    .st-emotion-cache-19r63f0 { /* Warning alert */
        background-color: #fffde7; /* Light yellow */
        color: #fbc02d;
        border-left: 5px solid #ffeb3b;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-19r63f0 p { /* Text inside warning alert */
        color: #fbc02d;
    }

    .st-emotion-cache-s1m2r8 { /* Error alert */
        background-color: #ffebee; /* Light red */
        color: #d32f2f;
        border-left: 5px solid #f44336;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-s1m2r8 p { /* Text inside error alert */
        color: #d32f2f;
    }

    /* Footer styling */
    .footer {
        text-align: center;
        color: #7f8c8d;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
        font-size: 0.9rem;
    }
    /* Timer specific styling */
    .timer-card {
        background-color: #ffffff;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .timer-card h4 {
        margin: 0;
        color: #34495e;
        font-size: 1.1rem;
    }
    .timer-card p {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #e74c3c; /* Red color for timer */
    }
</style>
""", unsafe_allow_html=True)


class StudentExamPage:
    def __init__(self):
        self.students = {}
        self.exam_questions = {}
        self.active_exams = {}
        self.student_credentials = {}
        self.load_student_data()
        logger.info(f"Initialized StudentExamPage. Students count: {len(self.students)}, Exams count: {len(self.exam_questions)}")
    
    def load_student_data(self):
        """Load student data from file"""
        try:
            if os.path.exists('students_data.json'):
                with open('students_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # st.info("Debugging: students_data.json loaded successfully.") # Debugging message - REMOVED
                    # st.json(data) # Debugging message - REMOVED

                    self.students = {k: {**v, 'id': k} for k, v in data.get('students', {}).items()}
                    self.exam_questions = data.get('questions', {}) # This likely contains the exam definitions
                    self.active_exams = data.get('active_exams', {}) # This should contain active exam statuses
                    self.student_credentials = data.get('credentials', {})
                    logger.info(f"Student data loaded. Students: {len(self.students)}, Exams: {len(self.exam_questions)}, Active Exams: {len(self.active_exams)}")
            else:
                logger.warning("students_data.json not found. Initializing empty data.")
                # st.warning("Debugging: students_data.json not found. Creating empty data structures.") # Debugging message - REMOVED
                self.students = {}
                self.exam_questions = {}
                self.active_exams = {}
                self.student_credentials = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding students_data.json: {e}", exc_info=True)
            st.error(f"❌ خطأ في تنسيق ملف بيانات الطلاب (students_data.json): {e}. يرجى التحقق من الملف أو حذفه وإعادة إنشائه من لوحة الأدمن.") # Specific error
            self.students = {}
            self.exam_questions = {}
            self.active_exams = {}
            self.student_credentials = {}
        except Exception as e:
            logger.error(f"Error loading student data: {e}", exc_info=True)
            self.students = {}
            self.exam_questions = {}
            self.active_exams = {}
            self.student_credentials = {}
            st.error(f"❌ حدث خطأ أثناء تحميل بيانات الطلاب: {e}")
    
    def save_student_data(self):
        """Save student data to file"""
        try:
            data = {
                'students': self.students,
                'credentials': self.student_credentials,
                'questions': self.exam_questions, # Save exam definitions here
                'exams': self.exam_questions, # Keep 'exams' key for backward compatibility if dashboard expects it
                'active_exams': self.active_exams # Save active exam statuses separately
            }
            with open('students_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Student data saved successfully.")
        except Exception as e:
            logger.error(f"Error saving student data: {e}", exc_info=True)
            st.error(f"❌ حدث خطأ أثناء حفظ بيانات الطلاب: {e}")

    def authenticate_student(self, username, password):
        """Authenticate student login"""
        # st.info(f"Debugging: Attempting to authenticate username: {username}") # Debugging message - REMOVED
        # st.json(self.student_credentials) # Debugging message - REMOVED
        if username in self.student_credentials:
            credentials = self.student_credentials[username]
            if credentials['password'] == password:
                student_id = credentials['student_id']
                if student_id in self.students:
                    self.students[student_id]['last_login'] = datetime.now().isoformat()
                    self.save_student_data()
                    # st.success(f"Debugging: Student {student_id} authenticated successfully.") # Debugging message - REMOVED
                    return self.students[student_id]
        # st.error("Debugging: Authentication failed.") # Debugging message - REMOVED
        return None

    def get_student_exam(self, student_id):
        """
        Get student's assigned exam details.
        Ensures 'id' key is present in the returned exam dictionary.
        """
        # st.info(f"Debugging: get_student_exam called for student_id: {student_id}") # Debugging message - REMOVED
        # st.json(self.students.get(student_id)) # Debugging message - REMOVED
        
        student_info = self.students.get(student_id)
        if student_info:
            current_exam_id = student_info.get('current_exam')
            # st.info(f"Debugging: Student {student_id} has current_exam_id: {current_exam_id}") # Debugging message - REMOVED
            # st.json(self.exam_questions) # Debugging message - REMOVED
            if current_exam_id and current_exam_id in self.exam_questions:
                exam_details = self.exam_questions[current_exam_id].copy()
                exam_details['id'] = current_exam_id # Explicitly add 'id' key here
                # st.success(f"Debugging: Found and returned exam details for exam ID: {current_exam_id}") # Debugging message - REMOVED
                # st.json(exam_details) # Debugging message - REMOVED
                return exam_details
        # st.warning(f"Debugging: No exam found for student {student_id} or exam not in exam_questions.") # Debugging message - REMOVED
        return None
    
    def start_exam_monitoring(self, student_id, exam_id):
        """Send command to dashboard to start monitoring for student"""
        try:
            command = {
                'action': 'start',
                'student_id': student_id,
                'exam_id': exam_id,
                'timestamp': datetime.now().isoformat(),
                'student_name': self.students.get(student_id, {}).get('name', 'غير معروف'), # Pass student name for AI service
                'exam_title': self.exam_questions.get(exam_id, {}).get('title', 'غير معروف') # Pass exam title for AI service
            }
            
            commands_file_path = 'dashboard_commands.json'
            if os.path.exists(commands_file_path):
                with open(commands_file_path, 'r', encoding='utf-8') as f:
                    try:
                        commands = json.load(f)
                    except json.JSONDecodeError:
                        commands = [] # Handle empty or malformed JSON
            else:
                commands = []
            
            commands.append(command)
            
            with open(commands_file_path, 'w', encoding='utf-8') as f:
                json.dump(commands, f, indent=2, ensure_ascii=False)
            
            # Update student's active exam status
            if student_id not in self.active_exams:
                self.active_exams[student_id] = {} # Initialize if not exists
            self.active_exams[student_id]['status'] = 'active'
            self.active_exams[student_id]['start_time'] = datetime.now().isoformat()
            self.active_exams[student_id]['exam_id'] = exam_id # Store exam_id in active_exams as well
            self.save_student_data() # Save the updated active_exams status

            logger.info(f"Monitoring start command sent for student {student_id}, exam {exam_id}.")
            # st.success("Debugging: Monitoring start command sent and active_exams updated.") # Debugging message - REMOVED
            return True
        except Exception as e:
            logger.error(f"Error starting exam monitoring: {e}", exc_info=True)
            st.error(f"❌ فشل في إرسال أمر بدء المراقبة: {e}")
            return False

    def stop_exam_monitoring(self, student_id, exam_id):
        """Send command to dashboard to stop monitoring for student"""
        try:
            command = {
                'action': 'stop',
                'student_id': student_id,
                'exam_id': exam_id,
                'timestamp': datetime.now().isoformat()
            }
            
            commands_file_path = 'dashboard_commands.json'
            if os.path.exists(commands_file_path):
                with open(commands_file_path, 'r', encoding='utf-8') as f:
                    try:
                        commands = json.load(f)
                    except json.JSONDecodeError:
                        commands = [] # Handle empty or malformed JSON
            else:
                commands = []
            
            commands.append(command)
            
            with open(commands_file_path, 'w', encoding='utf-8') as f:
                json.dump(commands, f, indent=2, ensure_ascii=False)
            
            # Update student's active exam status to submitted
            if student_id in self.active_exams:
                self.active_exams[student_id]['status'] = 'submitted'
                self.active_exams[student_id]['submitted_time'] = datetime.now().isoformat()
                # Optionally remove from active_exams or mark as finished
                # del self.active_exams[student_id] # Or mark as finished
                self.save_student_data()

            logger.info(f"Monitoring stop command sent for student {student_id}, exam {exam_id}.")
            # st.info("Debugging: Monitoring stop command sent and active_exams updated to 'submitted'.") # Debugging message - REMOVED
            return True
        except Exception as e:
            logger.error(f"Error stopping exam monitoring: {e}", exc_info=True)
            st.error(f"❌ فشل في إرسال أمر إيقاف المراقبة: {e}")
            return False


def main():
    student_exam_page_logic = StudentExamPage() # Instantiate the class

    # --- Student Login Logic ---
    # Check if a student is already logged in
    if 'logged_in_student' not in st.session_state or st.session_state['logged_in_student'] is None:
        st.markdown("""
        <div class="main-header">
            <h2>📝 صفحة امتحان الطالب</h2>
            <p>يرجى تسجيل الدخول للوصول إلى امتحاناتك</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🔐 تسجيل الدخول")
        login_username = st.text_input("اسم المستخدم", key="login_username_student")
        login_password = st.text_input("كلمة المرور", key="login_password_student", type="password")

        if st.button("🚪 تسجيل الدخول", key="login_button_student", use_container_width=True, type="primary"):
            if login_username and login_password:
                student_info = student_exam_page_logic.authenticate_student(login_username, login_password)
                if student_info:
                    st.session_state['logged_in_student'] = student_info
                    st.success(f"✅ مرحباً بك، {student_info['name']}!")
                    # Set exam start time in session state for countdown
                    st.session_state['exam_display_start_time'] = datetime.now().isoformat() # Store login time as a reference
                    st.session_state['exam_started'] = False # Not yet started, just logged in
                    time.sleep(1) # Small delay for success message to show
                    st.rerun() # Rerun to switch to exam view
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
            else:
                st.error("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور.")
        return # Exit main if not logged in, to show only login screen

    # --- Student Dashboard/Exam Display (Logged In) ---
    student = st.session_state['logged_in_student']
    student_id = student['id']
    
    # Hide sidebar during active exam for "screen freeze" effect
    if st.session_state.get('exam_started', False):
        st.markdown("<style>section.main[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
        # st.info("💡 تم إخفاء الشريط الجانبي لتجربة امتحان مركزة.") # Debug message - REMOVED
    else:
        st.markdown("<style>section.main[data-testid='stSidebar'] { display: block; }</style>", unsafe_allow_html=True) # Ensure it's visible when not in exam
        # st.info("💡 الشريط الجانبي مرئي. اضغط بدء الامتحان لإخفائه.") # Debug message - REMOVED

    # --- Sidebar content (only visible when exam is NOT started) ---
    with st.sidebar:
        if not st.session_state.get('exam_started', False):
            st.markdown("""
            <div class="exam-card">
                <h3>👤 معلومات الطالب</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**رقم الطالب:** {student['id']}")
            st.write(f"**الاسم:** {student['name']}")
            st.write(f"**اسم المستخدم:** {student.get('username', 'غير محدد')}")
            st.write(f"**الجامعة:** {student.get('university', 'غير محدد')}")
            st.write(f"**الحالة:** 🟢 {student.get('status', 'نشط')}") # Default to 'نشط'
            
            st.markdown("---")
            if st.button("🚪 تسجيل الخروج", key="logout_btn", use_container_width=True, type="secondary"):
                del st.session_state['logged_in_student']
                if 'exam_started' in st.session_state:
                    del st.session_state['exam_started']
                if 'exam_display_start_time' in st.session_state:
                    del st.session_state['exam_display_start_time']
                st.rerun()

    # --- Main Content ---
    st.markdown(f"""
    <div class="main-header">
        <h1>👨‍🎓 صفحة الطالب</h1>
        <h2>واجهة الامتحان</h2>
        <p>مرحباً بك {student['name']} - أنت الآن في نظام الامتحانات</p>
    </div>
    """, unsafe_allow_html=True)
    
    exam = student_exam_page_logic.get_student_exam(student_id)
    
    if not exam:
        st.markdown("""
        <div class="camera-warning">
            <h3>⚠️ لا يوجد امتحان مخصص لك</h3>
            <p>لم يتم تخصيص امتحان لك بعد. يرجى التواصل مع مشرفك.</p>
        </div>
        """, unsafe_allow_html=True)
        # st.info(f"Debugging: No exam object received from get_student_exam for student ID: {student_id}") # Debugging message - REMOVED
        # st.info(f"Debugging: Current student info from session_state: {student}") # Debugging message - REMOVED
        # st.info(f"Debugging: All students data: {student_exam_page_logic.students}") # Debugging message - REMOVED
        # st.info(f"Debugging: All exam questions data: {student_exam_page_logic.exam_questions}") # Debugging message - REMOVED
        # st.info(f"Debugging: All active exams data: {student_exam_page_logic.active_exams}") # Debugging message - REMOVED
        return
    
    # Check if exam has started, or is active according to backend
    exam_active_status_backend = student_exam_page_logic.active_exams.get(student_id, {}).get('status', 'not_started')
    
    # If the exam is not yet started or explicitly marked as not started by backend
    if not st.session_state.get('exam_started') and exam_active_status_backend == 'not_started':
        st.markdown(f"""
        <div class="exam-card" style="border-left: 5px solid #3498db;">
            <h2>📝 {exam['title']}</h2>
            <p><strong>المدة:</strong> {exam['duration']} دقيقة</p>
            <p><strong>عدد الأسئلة:</strong> {len(exam['questions'])} سؤال</p>
            <p><strong>تاريخ الإنشاء:</strong> {exam['created_at']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="camera-warning">
            <h3>⚠️ ملاحظة هامة!</h3>
            <p>عند بدء الامتحان:</p>
            <ul>
                <li>سيتم فتح الكاميرا للمراقبة.</li>
                <li>سيتم رصد سلوكك لمنع الغش.</li>
                <li>سيتم تسجيل أي سلوك مشبوه.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 بدء الامتحان", key="start_exam_btn", use_container_width=True, type="primary"):
            # st.info("📝 جاري إرسال أمر بدء المراقبة...") # Debug message - REMOVED
            if student_exam_page_logic.start_exam_monitoring(student_id, exam['id']):
                # Store actual exam start time
                st.session_state['exam_start_timestamp'] = time.time()
                st.session_state['exam_duration_seconds'] = exam['duration'] * 60 # Convert minutes to seconds
                st.session_state['exam_started'] = True
                st.success("🚀 تم بدء الامتحان! المراقبة نشطة...")
                time.sleep(2) # Give some time for messages to show
                st.rerun() # Rerun to activate exam view
            else:
                st.error("❌ فشل في بدء الامتحان. يرجى المحاولة مرة أخرى.")
    
    # If exam has started or is active
    elif st.session_state.get('exam_started') or exam_active_status_backend == 'active':
        # st.success("✅ وضع الامتحان نشط. المراقبة جارية.") # Debug message - REMOVED
        
        # --- Timer Display ---
        if 'exam_start_timestamp' in st.session_state and 'exam_duration_seconds' in st.session_state:
            elapsed_time = time.time() - st.session_state['exam_start_timestamp']
            remaining_time_seconds = max(0, st.session_state['exam_duration_seconds'] - elapsed_time)
            
            minutes = int(remaining_time_seconds // 60)
            seconds = int(remaining_time_seconds % 60)
            
            st.markdown(f"""
            <div class="timer-card">
                <h4>الوقت المتبقي للامتحان:</h4>
                <p>{minutes:02d}:{seconds:02d}</p>
            </div>
            """, unsafe_allow_html=True)

            # Auto-rerun for timer update (every second or few seconds)
            if remaining_time_seconds > 0:
                time.sleep(1) # Sleep to update timer
                st.rerun()
            else:
                if 'exam_finished_by_timer' not in st.session_state:
                    st.session_state['exam_finished_by_timer'] = True
                    st.warning("⏰ انتهى وقت الامتحان! سيتم تسليم إجاباتك تلقائياً.")
                    # Automatically submit if time runs out
                    submit_exam_automatically(student_exam_page_logic, student_id, exam)

        st.markdown(f"""
        <div class="camera-warning active">
            <h3>🎥 الكاميرا نشطة الآن!</h3>
            <p>النظام يراقب الامتحان. سيتم تسجيل أي سلوك مشبوه.</p>
            <div class="camera-placeholder">
                <img src="https://placehold.co/600x350/ADD8E6/000000?text=Live+Camera+Feed" alt="Live Camera Feed Placeholder" style="width:100%; border-radius: 8px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📝 أسئلة الامتحان")
        answers = {}
        
        # Collect answers from session state directly after all widgets are instantiated
        all_answered_from_state = True
        answers_from_state = {}

        for i, question in enumerate(exam['questions']):
            st.markdown(f"""
            <div class="question-card">
                <h4>السؤال {i+1}</h4>
                <p>{question['text']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            answer_key = f"answer_{question['id']}_{student_id}"
            current_answer = st.session_state.get(answer_key, "") # Retrieve answer from session state
            
            answer = st.text_area(
                f"إجابتك على السؤال {i+1}", 
                key=answer_key, # Unique key for each answer
                height=120,
                value=current_answer, # Populate with existing answer
                placeholder="اكتب إجابتك هنا...",
                help="يرجى تقديم إجابة مفصلة"
            )
            
            # Store answer back in answers_from_state
            if st.session_state[answer_key].strip():
                answers_from_state[question['id']] = st.session_state[answer_key]
            else:
                all_answered_from_state = False

        # Use answers_from_state for submission
        answers = answers_from_state # Update answers dictionary for submission logic

        if st.button("📤 تسليم الامتحان", key="submit_exam_btn", use_container_width=True, type="primary"):
            # Ensure the exam is not already submitted by timer
            if 'exam_finished_by_timer' in st.session_state and st.session_state['exam_finished_by_timer']:
                st.warning("⏰ تم تسليم الامتحان تلقائياً عند انتهاء الوقت.")
                # Proceed to cleanup and logout
                cleanup_and_logout(student_exam_page_logic, student_id, exam)
            elif all_answered_from_state:
                submit_exam_results(student_exam_page_logic, student_id, exam, answers)
            else:
                st.warning(f"⚠️ يرجى الإجابة على جميع الأسئلة. لقد أجبت على {len(answers)} من أصل {len(exam['questions'])} سؤال.")
    
    st.markdown("---")
    st.markdown(
        f"""
        <div class="footer">
        <p>نظام مراقبة الامتحانات المتقدم بالذكاء الاصطناعي v2.0</p>
        <p>واجهة الطالب</p>
        <p>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Helper functions for exam submission and cleanup ---
def submit_exam_results(student_exam_page_logic, student_id, exam, answers):
    st.success("✅ تم تسليم الامتحان بنجاح! سيتم مراجعة إجاباتك.")
    
    exam_result = {
        'student_id': student_id,
        'student_name': student_exam_page_logic.students.get(student_id, {}).get('name', 'غير معروف'),
        'exam_id': exam['title'],
        'submission_time': datetime.now().isoformat(),
        'answers': answers,
        'total_questions': len(exam['questions']),
        'answered_questions': len(answers)
    }
    
    try:
        results_file_path = 'exam_results.json'
        if os.path.exists(results_file_path):
            with open(results_file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            results = []
        
        results.append(exam_result)
        
        with open(results_file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        st.success("✅ تم حفظ إجاباتك بنجاح!")
        
    except Exception as e:
        logger.error(f"Failed to save answers: {e}", exc_info=True)
        st.error(f"❌ فشل في حفظ الإجابات: {e}")
    
    # Send command to stop monitoring
    if student_exam_page_logic.stop_exam_monitoring(student_id, exam['id']):
        st.info("⏹️ تم إيقاف المراقبة.")
    
    cleanup_and_logout(student_exam_page_logic, student_id, exam)

def cleanup_and_logout(student_exam_page_logic, student_id, exam):
    # Clear exam-related session state and log out student
    if 'exam_started' in st.session_state:
        del st.session_state['exam_started']
    if 'logged_in_student' in st.session_state:
        del st.session_state['logged_in_student']
    if 'exam_start_timestamp' in st.session_state:
        del st.session_state['exam_start_timestamp']
    if 'exam_duration_seconds' in st.session_state:
        del st.session_state['exam_duration_seconds']
    if 'exam_finished_by_timer' in st.session_state:
        del st.session_state['exam_finished_by_timer']
    
    # Clear all specific answer keys from session state
    if exam and 'questions' in exam:
        for question in exam['questions']:
            answer_key = f"answer_{question['id']}_{student_id}"
            if answer_key in st.session_state:
                del st.session_state[answer_key]

    time.sleep(3)
    st.rerun() # Rerun to go back to login screen

def submit_exam_automatically(student_exam_page_logic, student_id, exam):
    """Function to handle automatic exam submission when timer runs out."""
    st.info("⏰ يتم تسليم امتحانك تلقائيًا بسبب انتهاء الوقت.")
    
    # Collect current answers from session state
    answers = {}
    if exam and 'questions' in exam:
        for question in exam['questions']:
            answer_key = f"answer_{question['id']}_{student_id}"
            if answer_key in st.session_state and st.session_state[answer_key].strip():
                answers[question['id']] = st.session_state[answer_key]
    
    submit_exam_results(student_exam_page_logic, student_id, exam, answers)


if __name__ == "__main__":
    main()
