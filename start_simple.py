#!/usr/bin/env python3
"""
Simple System Runner
Advanced AI Exam Monitoring System
"""

import subprocess
import sys
import time
import os
import json

def print_banner():
    """Print system banner"""
    print("=" * 70)
    print("🎓 Advanced AI Exam Monitoring System v3.0")
    print("=" * 70)
    print("✨ Features:")
    print("   • Face movement detection")
    print("   • Emotion detection")
    print("   • Advanced audio analysis")
    print("   • Object detection")
    print("   • Screen freezing system")
    print("   • Student login system")
    print("   • Admin dashboard")
    print("   • Real-time monitoring")
    print("=" * 70)
    print()

def create_files():
    """Create necessary files"""
    print("📁 Creating required files...")

    # Create dashboard_data.json
    if not os.path.exists('dashboard_data.json'):
        dashboard_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "cheating_score": 0,
            "real_time_metrics": {
                "face_movements": 0,
                "audio_violations": 0,
                "object_violations": 0,
                "communication_attempts": 0,
                "suspicious_behavior": 0
            },
            "current_alerts": 0,
            "session_duration": 0,
            "incidents_count": 0,
            "dashboard_control": {
                "is_running": False,
                "current_student": None,
                "exam_start_time": None,
                "exam_duration": 0
            },
            "exam_termination": {
                "countdown": None,
                "terminated": False
            },
            "students": []
        }

        with open('dashboard_data.json', 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        print("✅ Created dashboard_data.json")

    # Create dashboard_commands.json
    if not os.path.exists('dashboard_commands.json'):
        with open('dashboard_commands.json', 'w') as f:
            json.dump([], f)
        print("✅ Created dashboard_commands.json")

    # Create students_data.json
    if not os.path.exists('students_data.json'):
        students_data = {
            "students": {},
            "credentials": {},
            "exams": {},
            "questions": {}
        }
        with open('students_data.json', 'w', encoding='utf-8') as f:
            json.dump(students_data, f, indent=2, ensure_ascii=False)
        print("✅ Created students_data.json")

def start_login_system():
    """Start login system"""
    print("🔐 Starting login system...")

    try:
        # Start login system on port 8501
        cmd = [sys.executable, "-m", "streamlit", "run", "login_system.py", "--server.port", "8501"]
        print(f"🚀 Running command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("✅ Login system started")
        print("🌐 Open browser at: http://localhost:8501")
        print("⏳ Waiting 10 seconds for initialization...")
        time.sleep(10)

        return process

    except Exception as e:
        print(f"❌ Failed to start login system: {e}")
        return None

def start_dashboard():
    """Start admin dashboard"""
    print("🌐 Starting admin dashboard...")

    try:
        # Start dashboard on port 8502
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8502"]
        print(f"🚀 Running command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("✅ Admin dashboard started")
        print("🌐 Open browser at: http://localhost:8502")
        print("⏳ Waiting 10 seconds for initialization...")
        time.sleep(10)

        return process

    except Exception as e:
        print(f"❌ Failed to start admin dashboard: {e}")
        return None

def main():
    """Main function"""
    print_banner()

    # Create files
    create_files()

    print("\n🎯 System Options:")
    print("1. Run login system only")
    print("2. Run admin dashboard only")
    print("3. Run full system")
    print("4. Exit")

    while True:
        try:
            choice = input("\nChoose an option (1-4): ").strip()

            if choice == "1":
                print("\n🔐 Starting login system only...")
                process = start_login_system()
                if process:
                    print("\n🎉 Login system started successfully!")
                    print("🌐 Open browser at: http://localhost:8501")
                    print("\n⚠️ Press Ctrl+C to stop system")
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print("\n⏹️ Stopping login system...")
                        process.terminate()
                break

            elif choice == "2":
                print("\n🌐 Starting admin dashboard only...")
                process = start_dashboard()
                if process:
                    print("\n🎉 Admin dashboard started successfully!")
                    print("🌐 Open browser at: http://localhost:8502")
                    print("\n⚠️ Press Ctrl+C to stop system")
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print("\n⏹️ Stopping admin dashboard...")
                        process.terminate()
                break

            elif choice == "3":
                print("\n🚀 Starting full system...")

                # Start login system first
                login_process = start_login_system()
                if not login_process:
                    print("❌ Failed to start login system")
                    break

                # Start dashboard
                dashboard_process = start_dashboard()
                if not dashboard_process:
                    print("❌ Failed to start admin dashboard")
                    break

                print("\n🎉 Full system started successfully!")
                print("🔐 Login system: http://localhost:8501")
                print("🌐 Admin dashboard: http://localhost:8502")
                print("\n💡 Usage Instructions:")
                print("1. Open browser at http://localhost:8501")
                print("2. Login as admin (admin/admin123) or student")
                print("3. Admin manages students and exams")
                print("4. Students take monitored exams")
                print("\n⚠️ Press Ctrl+C to stop system")

                try:
                    # Wait for processes
                    while True:
                        time.sleep(5)
                        if (login_process.poll() is not None or 
                            dashboard_process.poll() is not None):
                            print("⚠️ One of the systems has stopped")
                            break
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping system...")
                    if login_process:
                        login_process.terminate()
                    if dashboard_process:
                        dashboard_process.terminate()

                break

            elif choice == "4":
                print("\n👋 Thank you for using the system!")
                break

            else:
                print("❌ Invalid choice. Select 1-4")

        except KeyboardInterrupt:
            print("\n\n⏹️ System interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
