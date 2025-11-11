"""
Advanced Notification System
نظام الإشعارات المتطور
"""

import os
import time
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading
from queue import Queue
import logging
from typing import Dict, List, Optional

class NotificationSystem:
    """Advanced notification system for exam monitoring alerts"""
    
    def __init__(self):
        self.notification_queue = Queue()
        self.notification_history = []
        self.notification_settings = self.load_settings()
        
        # Notification types and priorities
        self.notification_types = {
            'critical': {
                'level': 1,
                'color': '🔴',
                'requires_immediate': True,
                'channels': ['email', 'sms', 'desktop', 'webhook']
            },
            'high': {
                'level': 2,
                'color': '🟠',
                'requires_immediate': True,
                'channels': ['email', 'desktop', 'webhook']
            },
            'medium': {
                'level': 3,
                'color': '🟡',
                'requires_immediate': False,
                'channels': ['email', 'desktop']
            },
            'low': {
                'level': 4,
                'color': '🟢',
                'requires_immediate': False,
                'channels': ['desktop']
            }
        }
        
        # Alert categories
        self.alert_categories = {
            'face_movement': 'medium',
            'suspicious_sounds': 'medium',
            'forbidden_object': 'high',
            'multiple_people': 'high',
            'student_absent': 'medium',
            'emotion_suspicious': 'medium',
            'system_error': 'critical',
            'connection_lost': 'high'
        }
        
        # Initialize notification channels
        self.setup_channels()
        
        # Start notification worker
        self.start_notification_worker()
        
        # Setup logging
        self.setup_logging()
    
    def load_settings(self):
        """Load notification settings from config"""
        default_settings = {
            'email': {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': '',
                'to_emails': []
            },
            'desktop': {
                'enabled': True,
                'sound_enabled': True,
                'popup_enabled': True
            },
            'general': {
                'max_notifications_per_hour': 50,
                'notification_cooldown': 300,  # 5 minutes
                'batch_notifications': True,
                'batch_interval': 60  # 1 minute
            }
        }
        
        # Try to load from file
        try:
            if os.path.exists('notification_settings.json'):
                with open('notification_settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_settings.items():
                        if key in default_settings:
                            default_settings[key].update(value)
        except Exception as e:
            print(f"⚠️ Could not load notification settings: {e}")
        
        return default_settings
    
    def setup_channels(self):
        """Setup notification channels"""
        self.channels = {}
        
        # Email channel
        if self.notification_settings['email']['enabled']:
            self.channels['email'] = EmailChannel(self.notification_settings['email'])
        
        # Desktop channel
        if self.notification_settings['desktop']['enabled']:
            self.channels['desktop'] = DesktopChannel(self.notification_settings['desktop'])
    
    def setup_logging(self):
        """Setup logging for notifications"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('notifications.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_notification_worker(self):
        """Start background notification worker"""
        self.worker_thread = threading.Thread(target=self.notification_worker, daemon=True)
        self.worker_thread.start()
    
    def notification_worker(self):
        """Background worker for processing notifications"""
        while True:
            try:
                if not self.notification_queue.empty():
                    notification = self.notification_queue.get()
                    self.process_notification(notification)
                    self.notification_queue.task_done()
                else:
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"Notification worker error: {e}")
                time.sleep(5)
    
    def send_notification(self, alert_type: str, message: str, data: Dict = None, priority: str = None):
        """Send notification for an alert"""
        if not priority:
            priority = self.alert_categories.get(alert_type, 'medium')
        
        notification = {
            'id': f"notif_{int(time.time())}_{hash(message) % 10000}",
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'priority': priority,
            'message': message,
            'data': data or {},
            'sent': False,
            'channels_used': []
        }
        
        # Add to queue
        self.notification_queue.put(notification)
        
        # Add to history
        self.notification_history.append(notification)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        self.logger.info(f"Notification queued: {alert_type} - {priority}")
        return notification['id']
    
    def process_notification(self, notification: Dict):
        """Process a single notification"""
        try:
            priority_info = self.notification_types[notification['priority']]
            channels_to_use = priority_info['channels']
            
            # Check rate limiting
            if not self.check_rate_limit(notification):
                self.logger.warning(f"Rate limit exceeded for notification: {notification['id']}")
                return
            
            # Send through appropriate channels
            for channel_name in channels_to_use:
                if channel_name in self.channels:
                    try:
                        success = self.channels[channel_name].send(notification)
                        if success:
                            notification['channels_used'].append(channel_name)
                            self.logger.info(f"Notification sent via {channel_name}: {notification['id']}")
                    except Exception as e:
                        self.logger.error(f"Failed to send via {channel_name}: {e}")
            
            notification['sent'] = True
            
        except Exception as e:
            self.logger.error(f"Failed to process notification: {e}")
    
    def check_rate_limit(self, notification: Dict) -> bool:
        """Check if notification is within rate limits"""
        current_time = time.time()
        cooldown = self.notification_settings['general']['notification_cooldown']
        max_per_hour = self.notification_settings['general']['max_notifications_per_hour']
        
        # Check cooldown for same type
        recent_same_type = [
            n for n in self.notification_history[-100:]
            if n['type'] == notification['type'] and 
            current_time - datetime.fromisoformat(n['timestamp']).timestamp() < cooldown
        ]
        
        if recent_same_type:
            return False
        
        # Check hourly limit
        hour_ago = current_time - 3600
        recent_notifications = [
            n for n in self.notification_history
            if datetime.fromisoformat(n['timestamp']).timestamp() > hour_ago
        ]
        
        if len(recent_notifications) >= max_per_hour:
            return False
        
        return True
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        if not self.notification_history:
            return {}
        
        stats = {
            'total_notifications': len(self.notification_history),
            'sent_notifications': len([n for n in self.notification_history if n['sent']]),
            'failed_notifications': len([n for n in self.notification_history if not n['sent']]),
            'priority_distribution': {},
            'type_distribution': {},
            'channel_usage': {},
            'recent_activity': []
        }
        
        # Priority distribution
        for notification in self.notification_history:
            priority = notification['priority']
            stats['priority_distribution'][priority] = stats['priority_distribution'].get(priority, 0) + 1
        
        # Type distribution
        for notification in self.notification_history:
            alert_type = notification['type']
            stats['type_distribution'][alert_type] = stats['type_distribution'].get(alert_type, 0) + 1
        
        # Channel usage
        for notification in self.notification_history:
            for channel in notification['channels_used']:
                stats['channel_usage'][channel] = stats['channel_usage'].get(channel, 0) + 1
        
        # Recent activity (last 24 hours)
        day_ago = datetime.now() - timedelta(days=1)
        recent = [
            n for n in self.notification_history
            if datetime.fromisoformat(n['timestamp']) > day_ago
        ]
        stats['recent_activity'] = recent
        
        return stats
    
    def test_notification(self, channel: str = 'desktop'):
        """Test notification system"""
        test_message = f"Test notification from AI Exam Monitor - {datetime.now().strftime('%H:%M:%S')}"
        return self.send_notification('system_test', test_message, {}, 'low')


class EmailChannel:
    """Email notification channel"""
    
    def __init__(self, settings: Dict):
        self.settings = settings
        self.smtp_server = settings['smtp_server']
        self.smtp_port = settings['smtp_port']
        self.username = settings['username']
        self.password = settings['password']
        self.from_email = settings['from_email']
        self.to_emails = settings['to_emails']
    
    def send(self, notification: Dict) -> bool:
        """Send email notification"""
        if not self.to_emails:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"AI Exam Monitor Alert: {notification['type'].replace('_', ' ').title()}"
            
            # Create email body
            body = self.create_email_body(notification)
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def create_email_body(self, notification: Dict) -> str:
        """Create HTML email body"""
        priority_info = {
            'critical': {'color': '#dc3545', 'icon': '🔴'},
            'high': {'color': '#fd7e14', 'icon': '🟠'},
            'medium': {'color': '#ffc107', 'icon': '🟡'},
            'low': {'color': '#28a745', 'icon': '🟢'}
        }
        
        priority = notification['priority']
        info = priority_info[priority]
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {info['color']}; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .footer {{ color: #6c757d; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{info['icon']} AI Exam Monitor Alert</h2>
                <p>Priority: {priority.upper()}</p>
            </div>
            
            <div class="content">
                <h3>Alert Details</h3>
                <p><strong>Type:</strong> {notification['type'].replace('_', ' ').title()}</p>
                <p><strong>Message:</strong> {notification['message']}</p>
                <p><strong>Time:</strong> {notification['timestamp']}</p>
            </div>
            
            <div class="details">
                <h4>Additional Information</h4>
                <pre>{json.dumps(notification['data'], indent=2)}</pre>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from the AI Exam Monitoring System.</p>
                <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html


class DesktopChannel:
    """Desktop notification channel"""
    
    def __init__(self, settings: Dict):
        self.settings = settings
        self.sound_enabled = settings['sound_enabled']
        self.popup_enabled = settings['popup_enabled']
    
    def send(self, notification: Dict) -> bool:
        """Send desktop notification"""
        try:
            if self.popup_enabled:
                self.show_popup(notification)
            
            if self.sound_enabled:
                self.play_sound(notification)
            
            return True
            
        except Exception as e:
            print(f"Desktop notification failed: {e}")
            return False
    
    def show_popup(self, notification: Dict):
        """Show desktop popup notification"""
        try:
            priority_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            icon = priority_icon.get(notification['priority'], '⚪')
            print(f"\n{icon} DESKTOP NOTIFICATION {icon}")
            print(f"Type: {notification['type']}")
            print(f"Priority: {notification['priority']}")
            print(f"Message: {notification['message']}")
            print(f"Time: {notification['timestamp']}")
            print("=" * 50)
            
        except Exception as e:
            print(f"Popup failed: {e}")
    
    def play_sound(self, notification: Dict):
        """Play notification sound"""
        try:
            priority = notification['priority']
            if priority in ['critical', 'high']:
                print("🔊 Playing high-priority sound")
            else:
                print("🔊 Playing normal notification sound")
                
        except Exception as e:
            print(f"Sound failed: {e}")


# Test function
if __name__ == "__main__":
    # Initialize notification system
    notifier = NotificationSystem()
    
    # Test notifications
    print("🧪 Testing notification system...")
    
    # Test different priority levels
    notifier.send_notification('face_movement', 'Student looking away for 5 seconds', {'student_id': 'S001'}, 'medium')
    notifier.send_notification('forbidden_object', 'Phone detected in frame', {'student_id': 'S002'}, 'high')
    notifier.send_notification('system_error', 'Camera connection lost', {}, 'critical')
    
    # Wait for notifications to process
    time.sleep(3)
    
    # Get statistics
    stats = notifier.get_notification_stats()
    print(f"\n📊 Notification Statistics:")
    print(f"Total: {stats.get('total_notifications', 0)}")
    print(f"Sent: {stats.get('sent_notifications', 0)}")
    print(f"Failed: {stats.get('failed_notifications', 0)}")
    
    print("\n✅ Notification system test completed!")
