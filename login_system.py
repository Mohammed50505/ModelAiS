#!/usr/bin/env python3
"""
نظام تسجيل الدخول - Login System
Advanced AI Exam Monitoring System - Login Interface
"""

import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import time

# استدعاء باقي الصفحات
import app
import student_exam_page

class LoginSystem:
    def __init__(self):
        self.admin_credentials = {
            'admin': {
                'password': 'admin123',
                'role': 'admin',
                'name': 'System Administrator'
            }
        }
        self.load_student_data()
    
    def load_student_data(self):
        """Load student data from file"""
        try:
            if os.path.exists('students_data.json'):
                with open('students_data.json', 'r') as f:
                    data = json.load(f)
                    self.students = data.get('students', {})
                    self.student_credentials = data.get('credentials', {})
                    self.exam_questions = data.get('questions', {})
            else:
                self.students = {}
                self.student_credentials = {}
                self.exam_questions = {}
        except Exception as e:
            print(f"Error loading student data: {e}")
            self.students = {}
            self.student_credentials = {}
            self.exam_questions = {}
    
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_admin(self, username, password):
        """Verify admin credentials"""
        if username in self.admin_credentials:
            if self.admin_credentials[username]['password'] == password:
                return self.admin_credentials[username]
        return None
    
    def verify_student(self, username, password):
        """Verify student credentials"""
        if username in self.student_credentials:
            if self.student_credentials[username]['password'] == password:
                student_id = self.student_credentials[username]['student_id']
                if student_id in self.students:
                    return self.students[student_id]
        return None
    
    def get_student_exam(self, student_id):
        """Get student's assigned exam"""
        if student_id in self.students:
            current_exam = self.students[student_id].get('current_exam')
            if current_exam and current_exam in self.exam_questions:
                return self.exam_questions[current_exam]
        return None

def main():
    # Configure page
    st.set_page_config(
        page_title="نظام تسجيل الدخول - Login System",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .login-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 2px solid #f0f0f0;
    }
    .role-selector {
        text-align: center;
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize login system
    login_system = LoginSystem()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 نظام مراقبة الامتحانات المتقدم</h1>
        <h2>Advanced AI Exam Monitoring System</h2>
        <p>اختر نوع المستخدم للدخول إلى النظام</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'login_role' not in st.session_state:
        st.session_state.login_role = None
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None
    
    # لو المستخدم خلاص مسجل دخول
    if st.session_state.logged_in_user:
        if st.session_state.login_role == 'admin':
            app.main()
            return
        elif st.session_state.login_role == 'student':
            student_exam_page.main()
            return

    # Role selection
    if not st.session_state.login_role:
        st.markdown("""
        <div class="role-selector">
            <h2>🔐 اختر نوع المستخدم</h2>
            <p>Select User Type</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👨‍💼 تسجيل دخول الأدمن", key="admin_btn", use_container_width=True):
                st.session_state.login_role = 'admin'
                st.rerun()
        
        with col2:
            if st.button("👨‍🎓 تسجيل دخول الطالب", key="student_btn", use_container_width=True):
                st.session_state.login_role = 'student'
                st.rerun()
    
    # Admin login
    elif st.session_state.login_role == 'admin':
        with st.form("admin_login_form"):
            admin_username = st.text_input("اسم المستخدم / Username", key="admin_username")
            admin_password = st.text_input("كلمة المرور / Password", type="password", key="admin_password")
            
            if st.form_submit_button("🔐 تسجيل الدخول / Login", use_container_width=True):
                if admin_username and admin_password:
                    admin_user = login_system.verify_admin(admin_username, admin_password)
                    if admin_user:
                        st.session_state.logged_in_user = admin_user
                        st.success("✅ تم تسجيل الدخول بنجاح! جاري التوجيه...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور خاطئة")
                else:
                    st.error("❌ يرجى ملء جميع الحقول")
        
        if st.button("🔙 العودة / Back", key="back_admin"):
            st.session_state.login_role = None
            st.rerun()
    
    # Student login
    elif st.session_state.login_role == 'student':
        with st.form("student_login_form"):
            student_username = st.text_input("اسم المستخدم / Username", key="student_username")
            student_password = st.text_input("كلمة المرور / Password", type="password", key="student_password")
            
            if st.form_submit_button("🔐 تسجيل الدخول / Login", use_container_width=True):
                if student_username and student_password:
                    student_user = login_system.verify_student(student_username, student_password)
                    if student_user:
                        st.session_state.logged_in_user = student_user
                        st.success("✅ تم تسجيل الدخول بنجاح! جاري التوجيه...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور خاطئة")
                else:
                    st.error("❌ يرجى ملء جميع الحقول")
        
        if st.button("🔙 العودة / Back", key="back_student"):
            st.session_state.login_role = None
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>Advanced AI Exam Monitoring System v2.0 | نظام مراقبة الامتحانات المتقدم</p>
        <p>Built with Streamlit & OpenCV | مبني بـ Streamlit & OpenCV</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
