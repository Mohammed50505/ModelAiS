import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import os
from collections import defaultdict
import logging
import sys
import random # Added this import to fix NameError: name 'random' is not defined

# Ensure UTF-8 encoding for standard output
sys.stdout.reconfigure(encoding='utf-8')

# Configure Streamlit page settings
st.set_page_config(
    page_title="لوحة تحكم نظام المراقبة بالذكاء الاصطناعي", # Updated title for clarity
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI/UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="st-emotion-cache"] {
        font-family: 'Inter', sans-serif;
        color: #333333; /* Darker text for readability */
        background-color: #f0f2f6; /* Light gray background */
    }

    /* General text and headers */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50; /* Darker headers */
        font-weight: 600;
    }

    /* Sidebar styling */
    .st-emotion-cache-vk33gh { /* Target the sidebar container */
        background-color: #ffffff; /* White background for sidebar */
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-right: 1px solid #e0e0e0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow */
    }
    .st-emotion-cache-vk33gh .st-emotion-cache-10q70t0 { /* Sidebar header */
        color: #3498db;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Buttons styling */
    .st-emotion-cache-use3lb { /* Primary button */
        background-color: #3498db; /* Blue */
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
        border: none;
    }
    .st-emotion-cache-use3lb:hover {
        background-color: #2980b9; /* Darker blue on hover */
        color: white;
    }

    .st-emotion-cache-v0u5xx { /* Secondary button */
        background-color: #ecf0f1; /* Light gray */
        color: #34495e; /* Dark gray text */
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
        border: 1px solid #bdc3c7;
    }
    .st-emotion-cache-v0u5xx:hover {
        background-color: #dde1e5; /* Slightly darker gray on hover */
        color: #34495e;
    }
    
    /* Text input and selectbox styling */
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

    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border-left: 5px solid #3498db; /* Blue accent */
    }
    .metric-card h5 {
        color: #3498db;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .metric-card p {
        font-size: 0.9rem;
        color: #555;
        line-height: 1.4;
    }

    /* Status cards */
    .status-card {
        background-color: #ffffff;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .status-card h2, .status-card h3, .status-card h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .status-card p {
        color: #7f8c8d;
    }

    /* Main header styling */
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

    /* Expander styling */
    .st-emotion-cache-p5m9py { /* Expander header */
        background-color: #ecf0f1;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        border: 1px solid #bdc3c7;
        margin-bottom: 0.5rem;
    }
    .st-emotion-cache-p5m9py .st-emotion-cache-1eq2l10 {
        color: #34495e;
        font-weight: 600;
    }

    /* Alert messages */
    .st-emotion-cache-1c8882q { /* Info alert */
        background-color: #e8f5e9;
        color: #388e3c;
        border-left: 5px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-1c8882q p {
        color: #388e3c;
    }
    .st-emotion-cache-19r63f0 { /* Warning alert */
        background-color: #fffde7;
        color: #fbc02d;
        border-left: 5px solid #ffeb3b;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-19r63f0 p {
        color: #fbc02d;
    }
    .st-emotion-cache-s1m2r8 { /* Error alert */
        background-color: #ffebee;
        color: #d32f2f;
        border-left: 5px solid #f44336;
        border-radius: 8px;
        padding: 1rem;
    }
    .st-emotion-cache-s1m2r8 p {
        color: #d32f2f;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #e0e0e0;
    }
    [data-testid="stMetricLabel"] > div {
        color: #7f8c8d;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #34495e;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1rem;
        font-weight: 600;
    }

    /* Plotly charts */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        background-color: #ffffff;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .main-header h2 {
            font-size: 1.8rem;
        }
        .main-header p {
            font-size: 1rem;
        }
        .st-emotion-cache-use3lb, .st-emotion-cache-v0u5xx {
            padding: 0.5rem 0.75rem;
            font-size: 0.9rem;
        }
        /* Make columns stack on small screens */
        [data-testid="stColumn"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedDashboardMonitor:
    def __init__(self):
        self.cheating_data = defaultdict(list)
        self.current_scores = defaultdict(int)
        self.alert_history = defaultdict(list)
        self.session_data = {}
        self.face_movement_data = defaultdict(list)
        self.sound_detection_data = defaultdict(list)
        
        # New real-time metrics
        self.real_time_metrics = {
            'face_movements': 0,
            'audio_violations': 0,
            'object_violations': 0,
            'communication_attempts': 0,
            'suspicious_behavior': 0
        }
        
        # Session data
        self.session_data = {
            'duration': 0,
            'incidents': 0,
            'last_update': '',
            'status': 'Active'
        }
        
        # Dashboard control
        self.dashboard_control = {
            'is_running': False,
            'current_student': None,
            'exam_start_time': None,
            'exam_duration': 0
        }
        
        # Students management with login credentials
        self.students = {}
        self.student_credentials = {}
        self.active_exams = {} # This will store actual active exam states
        self.exam_questions = {} # This will store exam definitions
        
        # Exam termination
        self.exam_termination = {
            'countdown': None,
            'terminated': False
        }
        
        # Load existing data
        self.load_student_data()
    
    def load_student_data(self):
        """Load student data from file"""
        try:
            if os.path.exists('students_data.json'):
                with open('students_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.students = {k: {**v, 'id': k} for k, v in data.get('students', {}).items()} # Ensure 'id' is in each student dict
                    self.student_credentials = data.get('credentials', {})
                    self.active_exams = data.get('active_exams', {}) # Correctly load active_exams
                    self.exam_questions = data.get('questions', {}) # Load exam definitions
            else:
                logger.warning("students_data.json not found. Initializing empty data.")
                self.students = {}
                self.exam_questions = {}
                self.active_exams = {}
                self.student_credentials = {}
        except Exception as e:
            logger.error(f"Error loading student data: {e}")
            st.error(f"خطأ في تحميل بيانات الطلاب: {e}") # Display error to user
    
    def save_student_data(self):
        """Save student data to file"""
        try:
            data = {
                'students': self.students,
                'credentials': self.student_credentials,
                'questions': self.exam_questions, # Save exam definitions
                'active_exams': self.active_exams # FIX: Save active exam states under 'active_exams' key
            }
            with open('students_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False) # ensure_ascii=False for Arabic characters
        except Exception as e:
            logger.error(f"Error saving student data: {e}")
            st.error(f"خطأ في حفظ بيانات الطلاب: {e}") # Display error to user
    
    def add_student_with_credentials(self, student_id, student_name, username, password, university):
        """Add new student with login credentials"""
        if student_id in self.students:
            st.error(f"❌ يوجد طالب بنفس الرقم التعريفي {student_id} بالفعل.")
            return False
        if username in self.student_credentials:
            st.error(f"❌ يوجد اسم مستخدم {username} بالفعل.")
            return False

        self.students[student_id] = {
            'name': student_name,
            'id': student_id,
            'username': username,
            'university': university,
            'status': 'active',
            'added_at': datetime.now().isoformat(),
            'last_login': None,
            'exam_history': [],
            'current_exam': None # Initialize current_exam
        }
        
        self.student_credentials[username] = {
            'password': password,
            'student_id': student_id
        }
        
        self.save_student_data()
        return True
    
    def authenticate_student(self, username, password):
        """Authenticate student login"""
        if username in self.student_credentials:
            if self.student_credentials[username]['password'] == password:
                student_id = self.student_credentials[username]['student_id']
                if student_id in self.students:
                    self.students[student_id]['last_login'] = datetime.now().isoformat()
                    self.save_student_data()
                    return self.students[student_id]
        return None
    
    def create_exam(self, exam_id, exam_title, questions, duration_minutes):
        """Create new exam"""
        if exam_id in self.exam_questions:
            st.error(f"❌ يوجد امتحان بنفس الرقم التعريفي {exam_id} بالفعل.")
            return False

        self.exam_questions[exam_id] = {
            'title': exam_title,
            'questions': questions,
            'duration': duration_minutes,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        self.save_student_data()
        return True
    
    def assign_exam_to_student(self, student_id, exam_id):
        """Assign exam to student"""
        if student_id not in self.students:
            st.error(f"❌ الطالب ذو الرقم {student_id} غير موجود.")
            return False
        if exam_id not in self.exam_questions:
            st.error(f"❌ الامتحان ذو الرقم {exam_id} غير موجود.")
            return False
        
        # Check if already assigned
        if self.students[student_id].get('current_exam') == exam_id: # Use .get() for safety
            st.info(f"الامتحان {self.exam_questions[exam_id]['title']} معين بالفعل للطالب {self.students[student_id]['name']}.")
            return True

        self.students[student_id]['current_exam'] = exam_id # Assign the exam ID to the student
        
        # Also update active_exams for this student
        self.active_exams[student_id] = {
            'exam_id': exam_id,
            'start_time': None,
            'status': 'assigned' # Initial status when assigned
        }
        self.save_student_data()
        st.success(f"✅ تم تعيين الامتحان '{self.exam_questions[exam_id]['title']}' للطالب {self.students[student_id]['name']} بنجاح!")
        return True
    
    def start_student_exam(self, student_id):
        """Start exam for student (updates active_exams in JSON)"""
        if student_id in self.active_exams:
            self.active_exams[student_id]['start_time'] = datetime.now().isoformat()
            self.active_exams[student_id]['status'] = 'active'
            self.save_student_data()
            return True
        return False
    
    def remove_student(self, student_id):
        """Remove student"""
        if student_id in self.students:
            student_name = self.students[student_id]['name']
            username = self.students[student_id].get('username')
            
            # Remove from students
            del self.students[student_id]
            
            # Remove credentials
            if username and username in self.student_credentials:
                del self.student_credentials[username]
            
            # Remove from active exams
            if student_id in self.active_exams:
                del self.active_exams[student_id]
            
            # Save updated data
            self.save_student_data()
            
            logger.info(f"🗑️ Student removed: {student_name} (ID: {student_id})")
            return True
        return False
        
    def load_dashboard_data(self):
        """Load real-time data from monitoring system"""
        try:
            # Load from JSON file
            if os.path.exists('dashboard_data.json'):
                with open('dashboard_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update real-time metrics
                if 'real_time_metrics' in data:
                    self.real_time_metrics = data['real_time_metrics']
                
                # Update cheating score
                if 'cheating_score' in data:
                    self.current_scores['current'] = data['cheating_score']
                
                # Update session duration
                if 'session_duration' in data:
                    self.session_data['duration'] = data['session_duration']
                
                # Update incidents count
                if 'incidents_count' in data:
                    self.session_data['incidents'] = data['incidents_count']
                
                # Update timestamp
                if 'timestamp' in data:
                    self.session_data['last_update'] = data['timestamp']
                
                # Update dashboard control
                if 'dashboard_control' in data:
                    self.dashboard_control = data['dashboard_control']
                
                # Update exam termination
                if 'exam_termination' in data:
                    self.exam_termination = data['exam_termination']
                
        except Exception as e:
            logger.error(f"Error loading dashboard data: {e}")
            st.error(f"خطأ في تحميل بيانات لوحة التحكم: {e}")
    
    def send_dashboard_command(self, action, **kwargs):
        """Send command to monitoring system"""
        try:
            command = {
                'action': action,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            
            # Create file if it doesn't exist
            if not os.path.exists('dashboard_commands.json'):
                with open('dashboard_commands.json', 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)
            
            # Read existing commands
            try:
                with open('dashboard_commands.json', 'r', encoding='utf-8') as f:
                    commands = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                commands = [] # Handle empty or malformed JSON
            
            # Add new command
            commands.append(command)
            
            # Write back to file
            with open('dashboard_commands.json', 'w', encoding='utf-8') as f:
                json.dump(commands, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            st.error(f"خطأ في إرسال الأمر: {e}")
            return False
        
    def load_log_data(self):
        """Load data from cheating log file"""
        try:
            if os.path.exists('cheating_log.txt'):
                with open('cheating_log.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                self.alert_history['all'] = [] # Clear previous alerts
                for line in lines:
                    if 'ALERT:' in line:
                        # Parse alert line
                        parts = line.split('ALERT:')
                        if len(parts) == 2:
                            timestamp_str_full = parts[0].strip()
                            alert_msg = parts[1].strip()
                            
                            # Extract datetime part from "YYYY-MM-DD HH:MM:SS - INFO - "
                            try:
                                timestamp_part = timestamp_str_full.split(' - INFO - ')[0].strip()
                                timestamp = datetime.strptime(timestamp_part, '%Y-%m-%d %H:%M:%S')
                                self.alert_history['all'].append({
                                    'timestamp': timestamp,
                                    'message': alert_msg,
                                    'type': self.categorize_alert(alert_msg)
                                })
                            except ValueError:
                                logger.warning(f"Could not parse timestamp from log line: {timestamp_str_full}")
                                continue
        except Exception as e:
            logger.error(f"Error loading log data: {e}")
            st.error(f"خطأ في تحميل بيانات السجل: {e}")
            
    def categorize_alert(self, message):
        """Categorize alert message with new categories"""
        message_lower = message.lower()
        if 'multiple people' in message_lower:
            return 'أكثر من شخص'
        elif 'looking away' in message_lower:
            return 'نظرة بعيدة'
        elif 'unauthorized object' in message_lower:
            return 'جسم غير مصرح به'
        elif 'not present' in message_lower:
            return 'غياب'
        elif 'talking' in message_lower:
            return 'تحدث'
        elif 'looking right' in message_lower or 'looking left' in message_lower or 'looking up' in message_lower or 'looking down' in message_lower:
            return 'حركة وجه'
        elif 'whispering' in message_lower or 'keyboard' in message_lower or 'paper' in message_lower:
            return 'أصوات مشبوهة'
        else:
            return 'أخرى'
            
    def get_alert_stats(self, date_range=None):
        """Get statistics about alerts within a date range"""
        if not self.alert_history['all']:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.alert_history['all'])
        if df.empty:
            return pd.DataFrame()

        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
        return df
        
    def create_alert_chart(self, date_range=None):
        """Create chart showing alert frequency over time"""
        df = self.get_alert_stats(date_range)
        if df.empty:
            return None
            
        hourly_counts = df.groupby('hour').size().reset_index(name='العدد')
        
        fig = px.line(hourly_counts, x='hour', y='العدد', 
                     title='تكرار التنبيهات حسب الساعة',
                     labels={'hour': 'الساعة', 'العدد': 'عدد التنبيهات'},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(height=400)
        return fig
        
    def create_alert_type_chart(self, date_range=None):
        """Create pie chart of alert types"""
        df = self.get_alert_stats(date_range)
        if df.empty:
            return None
            
        alert_counts = df['type'].value_counts()
        
        fig = px.pie(values=alert_counts.values, names=alert_counts.index,
                    title='توزيع التنبيهات حسب النوع',
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=400)
        return fig
        
    def create_timeline_chart(self, date_range=None):
        """Create timeline of alerts"""
        df = self.get_alert_stats(date_range)
        if df.empty:
            return None
            
        # Filter for recent data based on selected date range, or last 24 hours if no specific range
        if date_range and len(date_range) == 2:
            start_dt = datetime.combine(date_range[0], datetime.min.time())
            end_dt = datetime.combine(date_range[1], datetime.max.time())
            recent_df = df[(df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)]
        else: # Default to last 24 hours if no specific date range is selected
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_df = df[df['timestamp'] > cutoff_time]
        
        if recent_df.empty:
            return None
            
        fig = px.scatter(recent_df, x='timestamp', y='type', 
                        title='التنبيهات الأخيرة (حسب نطاق التاريخ)',
                        labels={'timestamp': 'الوقت', 'type': 'نوع التنبيه'},
                        color='type', # Color points by alert type
                        color_discrete_sequence=px.colors.qualitative.Alphabet)
        fig.update_layout(height=400)
        return fig
        
    def create_face_movement_chart(self):
        """Create chart showing face movement patterns (simulated)"""
        directions = ['يمين', 'يسار', 'أعلى', 'أسفل']
        movement_counts = [random.randint(5, 20) for _ in directions] # Simulated data
        
        fig = px.bar(x=directions, y=movement_counts,
                    title='أنماط حركة الوجه',
                    labels={'x': 'الاتجاه', 'y': 'العدد'},
                    color_discrete_sequence=px.colors.qualitative.Vivid)
        fig.update_layout(height=400)
        return fig
        
    def create_sound_detection_chart(self):
        """Create chart showing sound detection patterns (simulated)"""
        sound_types = ['همس', 'تحدث', 'لوحة مفاتيح', 'خشخشة ورق', 'اهتزاز هاتف']
        detection_counts = [random.randint(3, 15) for _ in sound_types] # Simulated data
        
        fig = px.bar(x=sound_types, y=detection_counts,
                    title='أنماط الكشف عن الأصوات',
                    labels={'x': 'نوع الصوت', 'y': 'عدد الكشف'},
                    color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(height=400)
        return fig

# Main function for the Streamlit application
def main():
    # Initialize monitor
    monitor = AdvancedDashboardMonitor()
    
    # Load data
    monitor.load_log_data()
    monitor.load_dashboard_data()
    
    # Auto-refresh every 3 seconds for real-time feel
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    # Only rerun if not in exam mode for performance
    if time.time() - st.session_state.last_refresh > 3 and 'exam_started' not in st.session_state:
        monitor.load_dashboard_data()
        st.session_state.last_refresh = time.time()
        st.rerun() # Rerun to update dashboard data


    # --- Sidebar ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #3498db;'>🎓 نظام إدارة الامتحانات</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Student Login Section
        st.markdown("### 👤 تسجيل دخول الطالب")
        
        student_username = st.text_input("اسم المستخدم", key="sidebar_student_username")
        student_password = st.text_input("كلمة المرور", key="sidebar_student_password", type="password")
        
        if st.button("🔐 تسجيل الدخول", key="sidebar_student_login_btn", use_container_width=True, type="primary"):
            if student_username and student_password:
                student = monitor.authenticate_student(student_username, student_password)
                if student:
                    st.success(f"✅ مرحباً {student['name']}!")
                    st.session_state['logged_in_student'] = student
                    st.session_state['student_exam_id'] = student.get('current_exam')
                    st.rerun()
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور خاطئة")
            else:
                st.error("❌ يرجى إدخال اسم المستخدم وكلمة المرور")
        
        # Show student exam if logged in
        if 'logged_in_student' in st.session_state and st.session_state['logged_in_student']:
            student = st.session_state['logged_in_student']
            st.markdown("---")
            st.markdown(f"### 👤 {student['name']}")
            
            if st.session_state.get('student_exam_id'):
                exam = monitor.exam_questions.get(st.session_state['student_exam_id'])
                if exam:
                    st.info(f"📝 الامتحان: {exam['title']}")
                    st.info(f"⏱️ المدة: {exam['duration']} دقيقة")
                    
                    if not st.session_state.get('exam_started', False):
                        if st.button("🚀 بدء الامتحان", key="sidebar_start_exam_btn", type="primary", use_container_width=True):
                            if monitor.start_student_exam(student['id']):
                                st.success("🚀 تم بدء الامتحان!")
                                st.session_state['exam_started'] = True
                                st.rerun()
                            else:
                                st.error("❌ فشل في بدء الامتحان")
                else:
                    st.warning("⚠️ لا يوجد امتحان مخصص لك حالياً.")
            else:
                st.info("لم يتم تخصيص امتحان لك بعد.")
            
            if st.button("🚪 تسجيل الخروج", key="sidebar_student_logout_btn", use_container_width=True, type="secondary"):
                del st.session_state['logged_in_student']
                if 'exam_started' in st.session_state:
                    del st.session_state['exam_started']
                if 'student_exam_id' in st.session_state:
                    del st.session_state['student_exam_id']
                st.rerun()
        
        # Admin Controls
        st.markdown("---")
        st.markdown("### ⚙️ تحكم الأدمن")
        
        # Refresh button
        if st.button("🔄 تحديث البيانات", key="sidebar_refresh_btn", use_container_width=True):
            monitor.load_log_data()
            monitor.load_dashboard_data()
            st.rerun()
            
        # Date range selector
        st.markdown("### 📅 نطاق التاريخ")
        today = datetime.now().date()
        default_start_date = today - timedelta(days=7)
        
        # Ensure value is a tuple (start_date, end_date)
        if 'date_range' not in st.session_state:
            st.session_state.date_range = (default_start_date, today)

        date_range = st.date_input(
            "اختر نطاق التاريخ",
            value=st.session_state.date_range,
            max_value=today,
            key="dashboard_date_range"
        )
        # Update session state when date range changes
        if date_range != st.session_state.date_range:
            st.session_state.date_range = date_range
            st.rerun() # Rerun to apply new date filter to charts

        # Ensure date_range is always a tuple of two dates
        if isinstance(date_range, (list, tuple)) and len(date_range) == 1:
            date_range = (date_range[0], date_range[0])
        elif not isinstance(date_range, (list, tuple)):
            date_range = (date_range, date_range)
        
        st.session_state['active_date_range'] = date_range # Store for use in charts


    # --- Main Content Area ---
    st.markdown("<div class='main-header'><h2>📊 لوحة تحكم نظام مراقبة الامتحانات بالذكاء الاصطناعي</h2><p>أهلاً بك يا أدمن 🎉</p></div>", unsafe_allow_html=True)

    # Dynamic Exam Display for Logged-in Student
    if 'logged_in_student' in st.session_state and st.session_state.get('exam_started', False):
        student = st.session_state['logged_in_student']
        exam_id = st.session_state.get('student_exam_id')
        exam = monitor.exam_questions.get(exam_id)
        
        if exam:
            st.markdown(f"""
            <div class="main-header" style="background-color: #e8f0f8; border-left: 8px solid #3498db; text-align: left;">
                <h2>📝 الامتحان: {exam['title']}</h2>
                <p>مرحباً {student['name']} - ابدأ الإجابة على الأسئلة</p>
                <p>المدة المتبقية: <strong>{exam['duration']} دقيقة</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.warning("⚠️ **تنبيه:** سيتم فتح الكاميرا لمراقبة الامتحان ومنع الغش، لا تحاول الغش!")
            
            # Simulated Camera Feed for Student (Placeholder)
            st.markdown("""
            <div class="status-card" style="border: 2px dashed #95a5a6;">
                <h3>📷 الكاميرا نشطة للمراقبة</h3>
                <p>فيديو الكاميرا الخاص بك يظهر هنا (لغرض المحاكاة)</p>
                <img src="https://placehold.co/600x350/ADD8E6/000000?text=Live+Camera+Feed" alt="Live Camera Feed Placeholder" style="width:100%; border-radius: 8px;">
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### أسئلة الامتحان")
            for i, question in enumerate(exam['questions']):
                st.markdown(f"""
                <div class="metric-card">
                    <h4>السؤال {i+1}:</h4>
                    <p>{question['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Answer input
                answer = st.text_area(f"إجابتك على السؤال {i+1}", 
                                    key=f"answer_{question['id']}_{student['id']}", 
                                    height=100,
                                    placeholder="اكتب إجابتك هنا...")
            
            # Submit exam button
            if st.button("📤 تسليم الامتحان", key="submit_exam_btn", type="primary", use_container_width=True):
                st.success("✅ تم تسليم الامتحان بنجاح! سيتم مراجعة إجاباتك.")
                time.sleep(2)
                del st.session_state['exam_started']
                del st.session_state['student_exam_id']
                st.rerun()
            
            st.markdown("---")
        else:
            st.error("❌ حدث خطأ: لا يمكن العثور على تفاصيل الامتحان.")

    elif 'logged_in_student' not in st.session_state or not st.session_state['logged_in_student']:
        # Admin Dashboard Sections
        col1, col2 = st.columns([2, 1]) # Adjusted column ratio for better layout
        
        with col1:
            st.markdown("### 📹 حالة المراقبة المباشرة")
            
            status_col1, status_col2, status_col3, status_col4 = st.columns(4)
            
            with status_col1:
                st.metric("الجلسات النشطة", "3", delta="+1")
                
            with status_col2:
                total_alerts_today = len([a for a in monitor.alert_history['all'] 
                                                   if a['timestamp'].date() == datetime.now().date()])
                st.metric("إجمالي تنبيهات اليوم", total_alerts_today)
                
            with status_col3:
                avg_score = 25  # This would be calculated from actual data
                st.metric("متوسط درجة الغش", f"{avg_score}/100", delta="-5")
                
            with status_col4:
                st.metric("تنبيهات حركة الوجه", f"{monitor.real_time_metrics['face_movements']}", 
                         delta=f"+{monitor.real_time_metrics['face_movements']}")
            
            st.markdown("### 📊 مقاييس الغش في الوقت الفعلي")
            
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            
            with metrics_col1:
                st.metric("انتهاكات الأجسام", f"{monitor.real_time_metrics['object_violations']}")
                st.metric("انتهاكات الصوت", f"{monitor.real_time_metrics['audio_violations']}")
            
            with metrics_col2:
                st.metric("محاولات التواصل", f"{monitor.real_time_metrics['communication_attempts']}")
                st.metric("سلوك مشبوه", f"{monitor.real_time_metrics['suspicious_behavior']}")
            
            with metrics_col3:
                st.metric("مدة الجلسة", f"{monitor.session_data['duration']:.1f} ثواني")
                st.metric("عدد الحوادث", f"{monitor.session_data['incidents']}")
                
            st.markdown("""
            <div class="status-card">
                <h3>📷 كاميرا الطالب</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if monitor.dashboard_control['is_running']:
                st.success("🟢 الكاميرا نشطة وتراقب")
                
                camera_placeholder = st.empty()
                
                with camera_placeholder.container():
                    mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(mock_frame, "تغذية الكاميرا المباشرة", (150, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(mock_frame, f"الطالب: {monitor.dashboard_control['current_student'] or 'غير معروف'}", 
                               (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                    cv2.putText(mock_frame, f"النقاط: {monitor.current_scores['current']}/100", 
                               (150, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
                    
                    mock_frame_rgb = cv2.cvtColor(mock_frame, cv2.COLOR_BGR2RGB)
                    st.image(mock_frame_rgb, channels="RGB", use_container_width=True)
                    
                    st.markdown("""
                    <div class="metric-card">
                        <h4>🎮 تحكم الكاميرا</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("📸 التقاط صورة", use_container_width=True, key="capture_img_btn"):
                            st.success("✅ تم التقاط الصورة!")
                    with col_b:
                        if st.button("🎥 تسجيل فيديو", use_container_width=True, key="record_vid_btn"):
                            st.success("✅ بدأ تسجيل الفيديو!")
                    with col_c:
                        if st.button("⏸️ إيقاف مؤقت", use_container_width=True, key="pause_cam_btn"):
                            st.info("⏸️ تم إيقاف الكاميرا مؤقتاً")
            else:
                st.markdown("""
                <div class="status-card">
                    <h4>📷 الكاميرا غير نشطة</h4>
                    <p>ابدأ المراقبة لتفعيل الكاميرا</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.image("https://placehold.co/640x480/666666/FFFFFF?text=Camera+Inactive", 
                        use_container_width=True)
                    
        with col2:
            st.markdown("### 🚨 التنبيهات الأخيرة")
            
            recent_alerts = monitor.alert_history['all'][-5:] if monitor.alert_history['all'] else []
            
            if recent_alerts:
                for alert in reversed(recent_alerts):
                    alert_type = alert['type']
                    color_map = {
                        'أكثر من شخص': '🔴',
                        'نظرة بعيدة': '🟡',
                        'جسم غير مصرح به': '🔴',
                        'غياب': '�',
                        'تحدث': '🟠',
                        'حركة وجه': '🟣',
                        'أصوات مشبوهة': '🟤',
                        'أخرى': '⚪'
                    }
                    
                    icon = color_map.get(alert_type, '⚪')
                    st.markdown(f"**{icon} {alert_type}**")
                    st.write(f"⏰ {alert['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"📝 {alert['message']}")
                    st.divider()
            else:
                st.info("✅ لا توجد تنبيهات حديثة")
                
        # Charts section
        st.markdown("---")
        st.markdown("### 📈 التحليلات والتقارير")
        
        col_charts1, col_charts2 = st.columns(2)
        
        with col_charts1:
            # Alert frequency chart
            alert_freq_chart = monitor.create_alert_chart(st.session_state['active_date_range'])
            if alert_freq_chart:
                st.plotly_chart(alert_freq_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات تنبيهات متاحة لإنشاء مخطط التكرار.")
                
            # Alert type distribution
            alert_type_chart = monitor.create_alert_type_chart(st.session_state['active_date_range'])
            if alert_type_chart:
                st.plotly_chart(alert_type_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات تنبيهات متاحة لإنشاء مخطط توزيع الأنواع.")
                
        with col_charts2:
            # Timeline chart
            timeline_chart = monitor.create_timeline_chart(st.session_state['active_date_range'])
            if timeline_chart:
                st.plotly_chart(timeline_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات تنبيهات حديثة متاحة للمخطط الزمني.")
                
            # Summary statistics
            st.markdown("### 📊 الإحصائيات الموجزة")
            
            df = monitor.get_alert_stats(st.session_state['active_date_range'])
            if not df.empty:
                total_alerts = len(df)
                today_alerts = len(df[df['timestamp'].date() == datetime.now().date()])
                unique_types = df['type'].nunique()
                
                st.metric("إجمالي التنبيهات", total_alerts)
                st.metric("تنبيهات اليوم", today_alerts)
                st.metric("أنواع التنبيهات", unique_types)
                
                # Most common alert type
                if not df['type'].empty:
                    most_common = df['type'].mode().iloc[0] if not df['type'].mode().empty else "لا يوجد"
                    st.metric("التنبيه الأكثر شيوعاً", most_common)
            else:
                st.info("لا توجد بيانات متاحة للإحصائيات.")
        
        # Dashboard Control Section
        st.markdown("---")
        
        st.markdown("""
        <div class="status-card">
            <h2>🎮 مركز التحكم الرئيسي</h2>
            <p>تحكم كامل في نظام المراقبة من هنا</p>
        </div>
        """, unsafe_allow_html=True)
        
        control_col1, control_col2 = st.columns([1, 1])
        
        with control_col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📹 التحكم في المراقبة</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if not monitor.dashboard_control['is_running']:
                st.markdown("""
                <div class="status-card" style="background-color: #ffebee; border-left: 5px solid #f44336;">
                    <h4>🔴 النظام متوقف</h4>
                    <p>اضغط على الزر أدناه لبدء المراقبة</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 بدء المراقبة", type="primary", use_container_width=True, key="start_monitoring_btn"):
                    active_students = [s for s in monitor.students.values() if s.get('current_exam')]
                    
                    if active_students:
                        student = active_students[0]
                        # FIX: Pass student_name and exam_title to dashboard command for AI service to use
                        exam_id_for_ai = student['current_exam']
                        exam_title_for_ai = monitor.exam_questions.get(exam_id_for_ai, {}).get('title', 'غير معروف')
                        monitor.send_dashboard_command('start', student_id=student['id'], student_name=student['name'], exam_id=exam_id_for_ai, exam_title=exam_title_for_ai)
                        
                        monitor.dashboard_control['is_running'] = True # Update local state immediately
                        monitor.dashboard_control['current_student'] = student['name']
                        monitor.dashboard_control['exam_start_time'] = time.time()
                        
                        # Start the exam automatically for the selected student
                        if monitor.start_student_exam(student['id']):
                            st.success(f"🚀 جاري بدء المراقبة والامتحان للطالب {student['name']}...")
                        else:
                             st.warning("⚠️ لم يتم بدء الامتحان تلقائياً. تأكد من تخصيص الامتحان.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.warning("⚠️ لا يوجد طلاب لديهم امتحانات نشطة. يرجى إضافة طالب وتخصيص امتحان أولاً.")
            else:
                st.markdown("""
                <div class="status-card" style="background-color: #e8f5e9; border-left: 5px solid #4caf50;">
                    <h4>🟢 النظام يعمل</h4>
                    <p>النظام يراقب حالياً</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("⏹️ إيقاف المراقبة", type="secondary", use_container_width=True, key="stop_monitoring_btn"):
                    # FIX: Pass current student and exam info for the stop command
                    student_id_to_stop = next((sid for sid, data in monitor.active_exams.items() if data.get('status') == 'active' and data.get('exam_id')), None)
                    if student_id_to_stop:
                        exam_id_to_stop = monitor.active_exams[student_id_to_stop].get('exam_id')
                        monitor.send_dashboard_command('stop', student_id=student_id_to_stop, exam_id=exam_id_to_stop)
                    else:
                        monitor.send_dashboard_command('stop') # Send general stop if no specific active exam found

                    monitor.dashboard_control['is_running'] = False # Update local state immediately
                    monitor.dashboard_control['current_student'] = None
                    monitor.dashboard_control['exam_start_time'] = None
                    st.success("⏹️ جاري إيقاف نظام المراقبة...")
                    time.sleep(2)
                    st.rerun()
            
            # Student selection for monitoring
            if monitor.students:
                student_options_for_monitor = {f"{s['id']} - {s['name']}": s['id'] for s in monitor.students.values()}
                # Ensure selectbox has options, and default to the current monitored student if exists
                current_monitored_student_id = next((s_id for s_id, s_data in monitor.students.items() if s_data.get('name') == monitor.dashboard_control.get('current_student')), None)
                
                initial_index = 0
                if current_monitored_student_id and current_monitored_student_id in student_options_for_monitor.values():
                    # Find the index of the current monitored student
                    keys = list(student_options_for_monitor.keys())
                    values = list(student_options_for_monitor.values())
                    try:
                        initial_index = values.index(current_monitored_student_id)
                    except ValueError:
                        initial_index = 0 # Fallback if not found

                selected_student_key = st.selectbox(
                    "اختر الطالب للمراقبة", 
                    list(student_options_for_monitor.keys()),
                    index=initial_index if student_options_for_monitor else None,
                    key="select_student_for_monitor"
                )
                
                if selected_student_key and st.button("🎯 بدء مراقبة الطالب المحدد", key="start_selected_student_monitor_btn", type="secondary", use_container_width=True):
                    student_id_to_monitor = student_options_for_monitor[selected_student_key]
                    student_name_to_monitor = monitor.students[student_id_to_monitor]['name']
                    # FIX: Pass exam_id and exam_title for the specific student
                    exam_id_for_ai = monitor.students[student_id_to_monitor].get('current_exam')
                    exam_title_for_ai = monitor.exam_questions.get(exam_id_for_ai, {}).get('title', 'غير معروف')
                    
                    if exam_id_for_ai:
                        monitor.send_dashboard_command('start', student_id=student_id_to_monitor, student_name=student_name_to_monitor, exam_id=exam_id_for_ai, exam_title=exam_title_for_ai)
                        monitor.dashboard_control['is_running'] = True
                        monitor.dashboard_control['current_student'] = student_name_to_monitor
                        monitor.dashboard_control['exam_start_time'] = time.time()
                        st.success(f"🚀 جاري بدء المراقبة للطالب {student_name_to_monitor}...")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.warning(f"⚠️ الطالب {student_name_to_monitor} ليس لديه امتحان مخصص بعد. يرجى تعيين امتحان أولاً.")


            st.markdown("#### الحالة الحالية:")
            status_color_display = "🟢" if monitor.dashboard_control['is_running'] else "🔴"
            st.write(f"**{status_color_display} الحالة:** {'يعمل' if monitor.dashboard_control['is_running'] else 'متوقف'}")
            
            if monitor.dashboard_control['current_student']:
                st.write(f"👤 **الطالب الحالي:** {monitor.dashboard_control['current_student']}")
            
            if monitor.dashboard_control['exam_start_time']:
                elapsed_time = time.time() - monitor.dashboard_control['exam_start_time']
                st.write(f"⏱️ **مدة المراقبة:** {elapsed_time:.1f} ثواني")
        
        with control_col2:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 إدارة الطلاب</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("➕ إضافة طالب جديد", expanded=True):
                new_student_id = st.text_input("رقم الطالب", key="new_student_id_input", placeholder="مثال: A001")
                new_student_name = st.text_input("اسم الطالب", key="new_student_name_input", placeholder="مثال: أحمد محمد")
                new_university = st.text_input("اسم الجامعة", key="new_university_input", placeholder="مثال: جامعة القاهرة")
                new_username = st.text_input("اسم المستخدم", key="new_username_input", placeholder="مثال: ahmed123")
                new_password = st.text_input("كلمة المرور", key="new_password_input", type="password", placeholder="كلمة المرور")
                
                if st.button("➕ إضافة الطالب", key="add_student_btn", use_container_width=True, type="primary"):
                    if new_student_id and new_student_name and new_university and new_username and new_password:
                        if monitor.add_student_with_credentials(new_student_id, new_student_name, new_username, new_password, new_university):
                            st.success(f"✅ تم إضافة الطالب {new_student_name} بنجاح!")
                            st.info(f"اسم المستخدم: {new_username} | كلمة المرور: {new_password}")
                            time.sleep(2)
                            st.rerun()
                        # Error messages are handled inside add_student_with_credentials
                    else:
                        st.error("❌ يرجى ملء جميع الحقول.")
            
            with st.expander("📝 إنشاء امتحان جديد", expanded=False):
                exam_id = st.text_input("رقم الامتحان", key="create_exam_id", placeholder="مثال: EXAM001")
                exam_title = st.text_input("عنوان الامتحان", key="create_exam_title", placeholder="مثال: امتحان الرياضيات")
                exam_duration = st.number_input("مدة الامتحان (دقائق)", key="create_exam_duration", min_value=15, max_value=180, value=60)
                
                st.markdown("##### إضافة الأسئلة (5 أسئلة افتراضية)")
                questions = []
                for i in range(5):
                    question_text = st.text_area(f"السؤال {i+1}", key=f"q_text_{i}", placeholder="اكتب السؤال هنا...")
                    if question_text.strip():
                        questions.append({
                            'id': f"Q{i+1}",
                            'text': question_text,
                            'type': 'text'
                        })
                
                if st.button("📝 إنشاء الامتحان", key="create_exam_main_btn", use_container_width=True, type="primary"):
                    if exam_id and exam_title and questions:
                        if monitor.create_exam(exam_id, exam_title, questions, exam_duration):
                            st.success(f"✅ تم إنشاء الامتحان '{exam_title}' بنجاح!")
                            time.sleep(2)
                            st.rerun()
                        # Error messages are handled inside create_exam
                    else:
                        st.error("❌ يرجى ملء حقول رقم وعنوان الامتحان وإضافة سؤال واحد على الأقل.")
            
            if monitor.students and monitor.exam_questions:
                with st.expander("📋 تعيين امتحان لطالب", expanded=False):
                    selected_student_assign = st.selectbox("اختر الطالب", 
                                                   list(monitor.students.keys()),
                                                   format_func=lambda x: f"{x} - {monitor.students[x]['name']}",
                                                   key="assign_exam_student_select")
                    
                    selected_exam_assign = st.selectbox("اختر الامتحان", 
                                                list(monitor.exam_questions.keys()),
                                                format_func=lambda x: f"{x} - {monitor.exam_questions[x]['title']}",
                                                key="assign_exam_select")
                    
                    if st.button("📋 تعيين الامتحان", key="assign_exam_btn", use_container_width=True, type="primary"):
                        if monitor.assign_exam_to_student(selected_student_assign, selected_exam_assign):
                            # Success message moved inside assign_exam_to_student
                            time.sleep(2)
                            st.rerun()
                        # Error messages are handled inside assign_exam_to_student
            else:
                st.info("⚠️ لا يوجد طلاب أو امتحانات لتعيينها. يرجى إضافة طالب وامتحان أولاً.")
            
            if monitor.students:
                with st.expander("🗑️ حذف طالب", expanded=False):
                    student_to_remove_id = st.selectbox("اختر الطالب للحذف", 
                                                   list(monitor.students.keys()),
                                                   format_func=lambda x: f"{x} - {monitor.students[x]['name']}",
                                                   key="remove_student_select")
                    
                    if student_to_remove_id:
                        # Display confirmation message before deletion
                        st.warning(f"هل أنت متأكد من حذف الطالب {monitor.students[student_to_remove_id]['name']}؟ لا يمكن التراجع عن هذا الإجراء.")
                        if st.button("تأكيد الحذف", key="confirm_delete_btn", use_container_width=True, type="secondary"):
                            if monitor.remove_student(student_to_remove_id):
                                st.success(f"✅ تم حذف الطالب {monitor.students[student_to_remove_id]['name']} بنجاح!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ فشل في حذف الطالب.")
            
            st.markdown("---")
            st.markdown("#### 📋 الطلاب المسجلون")
            if monitor.students:
                for student_id, student in monitor.students.items():
                    current_exam_title = "لا يوجد"
                    exam_status_display = "لا يوجد امتحان"
                    if student.get('current_exam') and student['current_exam'] in monitor.exam_questions:
                        current_exam_title = monitor.exam_questions[student['current_exam']]['title']
                        # FIX: Check active_exams for status, not the dashboard's internal active_exams
                        exam_status_display = monitor.active_exams.get(student_id, {}).get('status', 'معين')

                    last_login = "لم يسجل دخول"
                    if student.get('last_login'):
                        try:
                            login_time = datetime.fromisoformat(student['last_login'])
                            last_login = login_time.strftime("%Y-%m-%d %H:%M")
                        except ValueError:
                            pass # Handle potential parsing errors

                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 5px solid #2ecc71;">
                        <h5>👤 {student['name']} (ID: {student_id})</h5>
                        <div style="text-align: left;">
                            <p><strong>اسم المستخدم:</strong> {student.get('username', 'غير محدد')}</p>
                            <p><strong>الجامعة:</strong> {student.get('university', 'غير محدد')}</p>
                            <p><strong>الحالة:</strong> 🟢 {student['status']}</p>
                            <p><strong>آخر تسجيل دخول:</strong> {last_login}</p>
                            <p><strong>الامتحان الحالي:</strong> {current_exam_title}</p>
                            <p><strong>حالة الامتحان:</strong> {exam_status_display}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_sa, col_sb = st.columns(2)
                    with col_sa:
                        if st.button(f"📊 تقرير {student['name']}", key=f"report_{student_id}_btn", use_container_width=True):
                            st.session_state['show_student_report'] = student_id
                            st.rerun()
                    with col_sb:
                        if st.button(f"🗑️ حذف {student['name']} (مباشر)", key=f"delete_student_inline_{student_id}_btn", use_container_width=True, type="secondary"):
                            if monitor.remove_student(student_id): # Direct call, assuming immediate delete is desired here
                                st.success(f"✅ تم حذف الطالب {student['name']} بنجاح!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ فشل في حذف الطالب.")
                
                # Show student report if requested
                if 'show_student_report' in st.session_state and st.session_state['show_student_report'] in monitor.students:
                    student_id_for_report = st.session_state['show_student_report']
                    student_for_report = monitor.students[student_id_for_report]
                    st.markdown("---")
                    st.markdown(f"""
                    <div class="status-card" style="border-left: 5px solid #f39c12;">
                        <h3>📊 تقرير الطالب: {student_for_report['name']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    report_col1, report_col2 = st.columns(2)
                    with report_col1:
                        st.write(f"**رقم الطالب:** {student_for_report['id']}")
                        st.write(f"**الاسم:** {student_for_report['name']}")
                        st.write(f"**اسم المستخدم:** {student_for_report.get('username', 'غير محدد')}")
                        st.write(f"**الجامعة:** {student_for_report.get('university', 'غير محدد')}")
                        st.write(f"**الحالة:** {student_for_report['status']}")
                    
                    with report_col2:
                        st.write(f"**تاريخ الإضافة:** {student_for_report.get('added_at', 'غير محدد')}")
                        st.write(f"**آخر تسجيل دخول:** {student_for_report.get('last_login', 'لم يسجل دخول')}")
                        st.write(f"**الامتحان الحالي:** {monitor.exam_questions.get(student_for_report.get('current_exam', ''), {}).get('title', 'لا يوجد')}")
                    
                    if student_for_report.get('exam_history'):
                        st.subheader("📚 تاريخ الامتحانات")
                        for exam_entry in student_for_report['exam_history']:
                            st.write(f"- {exam_entry}")
                    
                    if st.button("❌ إغلاق التقرير", key="close_report_btn", use_container_width=True):
                        del st.session_state['show_student_report']
                        st.rerun()
            else:
                st.info("📝 لا يوجد طلاب مسجلون حالياً.")
        
        # Exam Termination Warning
        if monitor.exam_termination['countdown'] and monitor.exam_termination['countdown'] > 0:
            st.markdown("---")
            st.error(f"🚨 **تنبيه إنهاء الامتحان!**")
            st.error(f"⏰ **سينتهي الامتحان خلال {monitor.exam_termination['countdown']:.1f} ثواني!**")
            
            progress = (monitor.exam_termination['countdown'] / 10.0) # Assuming 10 seconds total warning
            st.progress(progress)
            
            st.write(f"**الوقت المتبقي: {monitor.exam_termination['countdown']:.1f} ثواني**")
        
        if monitor.exam_termination['terminated']:
            st.markdown("---")
            st.error("🚨 **تم إنهاء الامتحان!** تم استبعاد الطالب بسبب الغش!")
            st.info("تحقق من 'final_exam_report.json' للحصول على تقرير مفصل.")
                
        # New Advanced Features Section
        st.markdown("---")
        st.markdown("### 🔍 ميزات الكشف المتقدمة")
        
        adv_col1, adv_col2 = st.columns(2)
        
        with adv_col1:
            st.markdown("#### 👁️ تتبع حركة الوجه")
            
            movement_col1, movement_col2, movement_col3, movement_col4 = st.columns(4)
            
            with movement_col1:
                st.metric("يمين", "15", delta="+3")
            with movement_col2:
                st.metric("يسار", "12", delta="+1")
            with movement_col3:
                st.metric("أعلى", "8", delta="+2")
            with movement_col4:
                st.metric("أسفل", "10", delta="+1")
                
            face_movement_chart = monitor.create_face_movement_chart()
            if face_movement_chart:
                st.plotly_chart(face_movement_chart, use_container_width=True)
                
            st.markdown("##### ⚙️ إعدادات حركة الوجه")
            movement_threshold = st.slider("عتبة الحركة (بالثواني)", 2, 5, 3, key="movement_threshold_slider")
            movement_sensitivity = st.slider("حساسية الحركة (بالبكسل)", 30, 100, 50, key="movement_sensitivity_slider")
            
        with adv_col2:
            st.markdown("#### 🔊 تحليل الكشف عن الأصوات")
            
            sound_col1, sound_col2 = st.columns(2)
            
            with sound_col1:
                st.metric("همس", "8", delta="+2")
                st.metric("تحدث", "12", delta="+1")
                st.metric("لوحة مفاتيح", "20", delta="+5")
                
            with sound_col2:
                st.metric("خشخشة ورق", "15", delta="+3")
                st.metric("اهتزاز هاتف", "5", delta="+1")
                st.metric("أخرى", "3", delta="0")
                
            sound_detection_chart = monitor.create_sound_detection_chart()
            if sound_detection_chart:
                st.plotly_chart(sound_detection_chart, use_container_width=True)
                
            st.markdown("##### ⚙️ إعدادات الكشف عن الأصوات")
            audio_sensitivity = st.slider("حساسية الصوت", 0.1, 2.0, 1.0, 0.1, key="audio_sensitivity_slider")
            noise_reduction = st.checkbox("تفعيل خاصية إلغاء الضوضاء", value=True, key="noise_reduction_checkbox")
                
        # System Settings section (Global settings)
        st.markdown("---")
        st.markdown("### ⚙️ إعدادات النظام")
        
        settings_col1, settings_col2, settings_col3 = st.columns(3)
        
        with settings_col1:
            st.markdown("##### حساسية الكشف")
            face_threshold = st.slider("عتبة الابتعاد بالوجه (بالثواني)", 3, 10, 5, key="face_away_threshold_slider")
            absence_threshold = st.slider("عتبة الغياب (بالثواني)", 2, 5, 3, key="absence_threshold_slider")
            # Movement threshold is already in advanced section, removed duplication
            
        with settings_col2:
            st.markdown("##### عقوبات النقاط")
            multiple_people_penalty = st.slider("أكثر من شخص", 10, 30, 20, key="multiple_people_penalty_slider")
            forbidden_object_penalty = st.slider("جسم محظور", 15, 35, 25, key="forbidden_object_penalty_slider")
            face_movement_penalty = st.slider("حركة الوجه", 10, 25, 15, key="face_movement_penalty_slider")
            suspicious_sounds_penalty = st.slider("أصوات مشبوهة", 10, 25, 15, key="suspicious_sounds_penalty_slider")
            
        with settings_col3:
            st.markdown("##### الإشعارات")
            email_alerts = st.checkbox("تنبيهات البريد الإلكتروني", value=True, key="email_alerts_checkbox")
            sms_alerts = st.checkbox("تنبيهات الرسائل النصية القصيرة", value=False, key="sms_alerts_checkbox")
            desktop_notifications = st.checkbox("إشعارات سطح المكتب", value=True, key="desktop_notifications_checkbox")
            face_movement_alerts = st.checkbox("تنبيهات حركة الوجه", value=True, key="face_movement_alerts_checkbox")
            sound_detection_alerts = st.checkbox("تنبيهات الكشف عن الأصوات", value=True, key="sound_detection_alerts_checkbox")
            
        if st.button("💾 حفظ الإعدادات", key="save_settings_btn", use_container_width=True, type="primary"):
            st.success("✅ تم حفظ الإعدادات بنجاح!")
            # In a real app, you would save these settings to a config file or database
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Advanced AI Exam Monitoring System v2.0 | مبني باستخدام Streamlit & OpenCV</p>
        <p>الميزات: تتبع حركة الوجه، كشف الصوت المحسن، كشف الغش المتقدم</p>
        <p>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
