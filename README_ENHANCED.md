# 🎓 Advanced AI Exam Monitoring System v3.0

## نظام مراقبة الامتحانات المتقدم - النسخة المحسنة

### ✨ New Features in v3.0

#### 🔐 **Enhanced Login System**
- **Separate Login Interface**: Dedicated login page for admin and students
- **Admin Credentials**: Username: `admin`, Password: `admin123`
- **Student Authentication**: Individual student accounts with username/password
- **Role-based Access**: Different interfaces for admin and students

#### 🖥️ **Screen Lock System**
- **Full-Screen Lock**: Prevents cheating during exams
- **Anti-Alt+Tab**: Blocks keyboard shortcuts and window switching
- **Visual Warnings**: Clear instructions and warnings for students
- **Timer Display**: Shows elapsed exam time
- **Automatic Unlock**: Releases lock when exam is submitted

#### 🏫 **University Management**
- **University Field**: Added university name for each student
- **Enhanced Student Profiles**: More detailed student information
- **Better Organization**: Improved student data structure

#### 👥 **Multi-Student Support**
- **Concurrent Monitoring**: Monitor multiple students simultaneously
- **Individual Tracking**: Separate cheating scores and reports per student
- **Student Isolation**: Each student has independent exam session

#### 🎯 **Enhanced Dashboard Control**
- **Real-time Monitoring**: Live camera feed and metrics
- **Student Management**: Add, remove, and manage students
- **Exam Creation**: Create and assign exams to students
- **Live Reports**: Real-time cheating detection reports

### 🚀 **How to Use**

#### **1. Start the System**
```bash
python start_system.py
```

#### **2. Access the System**
- **Login System**: http://localhost:8501
- **Admin Dashboard**: http://localhost:8502 (after admin login)

#### **3. Admin Workflow**
1. Login with `admin/admin123`
2. Add new students with university information
3. Create exams with questions
4. Assign exams to students
5. Start monitoring from dashboard

#### **4. Student Workflow**
1. Students login with their credentials
2. View assigned exam
3. Click "Start Exam" to begin
4. Screen locks automatically
5. Camera monitoring starts
6. Answer questions and submit

### 🔧 **System Architecture**

#### **Core Components**
- `login_system.py` - Main login interface
- `student_exam_page.py` - Student exam interface
- `screen_lock.py` - Screen locking system
- `main.py` - AI monitoring system
- `app.py` - Admin dashboard
- `start_system.py` - System controller

#### **Data Files**
- `students_data.json` - Student and exam data
- `dashboard_data.json` - Real-time monitoring data
- `dashboard_commands.json` - System commands
- `exam_results.json` - Exam submissions
- `screen_lock_sessions.json` - Lock session logs

### 🎮 **Control Features**

#### **Dashboard Controls**
- Start/Stop monitoring
- Add/Remove students
- Create/Assign exams
- View real-time metrics
- Access student reports

#### **Monitoring Features**
- Face movement detection
- Audio analysis
- Object detection
- Emotion recognition
- Cheating score calculation

#### **Security Features**
- Screen locking
- Process monitoring
- Anti-cheating measures
- Session logging

### 📊 **Real-time Metrics**

#### **Cheating Detection**
- Face movements (right, left, up, down)
- Audio violations
- Object violations
- Communication attempts
- Suspicious behavior

#### **Live Reports**
- Current cheating score
- Session duration
- Incident count
- Alert history
- Student status

### 🔒 **Security Measures**

#### **Screen Lock**
- Full-screen overlay
- Keyboard shortcut blocking
- Mouse click prevention
- Window switching prevention
- Automatic timer display

#### **Monitoring**
- Camera surveillance
- Audio recording
- Behavior analysis
- Incident logging
- Real-time alerts

### 🌐 **Access Points**

#### **Ports Used**
- **8501**: Login system
- **8502**: Admin dashboard
- **Camera**: Webcam access
- **Audio**: Microphone access

#### **Network Access**
- Localhost only (for security)
- No external connections
- Secure data storage
- Encrypted communications

### 📝 **Configuration**

#### **Admin Settings**
- Detection sensitivity
- Score penalties
- Alert thresholds
- Notification settings

#### **Student Settings**
- Exam duration
- Question count
- Submission rules
- Monitoring level

### 🚨 **Troubleshooting**

#### **Common Issues**
1. **Camera not working**: Check webcam permissions
2. **Audio issues**: Verify microphone access
3. **Screen lock problems**: Ensure tkinter is installed
4. **Dashboard errors**: Check port availability

#### **Solutions**
- Restart the system
- Check dependencies
- Verify file permissions
- Clear browser cache

### 🔄 **Updates and Maintenance**

#### **Regular Tasks**
- Update student data
- Review monitoring logs
- Check system health
- Backup data files

#### **System Updates**
- Monitor for new versions
- Update dependencies
- Test new features
- Maintain security

### 📞 **Support**

#### **Documentation**
- This README file
- Code comments
- System logs
- Error messages

#### **Contact**
- Check system logs
- Review error messages
- Test individual components
- Verify configurations

---

## 🎉 **System Ready for Production Use!**

The Enhanced AI Exam Monitoring System v3.0 is now fully equipped with:
- ✅ Advanced cheating detection
- ✅ Secure student authentication
- ✅ Screen locking system
- ✅ Multi-student support
- ✅ Real-time monitoring
- ✅ Comprehensive reporting
- ✅ Professional interface
- ✅ University management

**Ready to deploy in educational institutions!** 🚀
