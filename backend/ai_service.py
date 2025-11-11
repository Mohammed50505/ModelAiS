# ai_service/main.py (هذا ملف منفصل لخدمة الذكاء الاصطناعي الخاصة بك)

import requests
import json
from datetime import datetime
import time
import random

# عنوان الـ FastAPI Backend الخاص بك
FASTAPI_BACKEND_URL = "http://localhost:8000" # تأكد من أن هذا هو العنوان الصحيح للباك إند

# (اختياري) لو عايز تبعت توكن مصادقة مع كل طلب من الـ AI Service
# في نظام حقيقي، لازم الـ AI Service يعمل مصادقة للحصول على التوكن ده
# لكن للمثال ده، هنفترض إن الـ endpoint بتاع proctor_updates مش بيحتاج مصادقة حالياً
# أو إن الـ AI Service عنده توكن ثابت
AI_SERVICE_AUTH_TOKEN = "your_ai_service_secret_token_here" # استبدلها بتوكن حقيقي لو هتحتاج مصادقة

def send_proctor_update(session_id: str, update_data: dict):
    """
    دالة لإرسال تحديثات المراقبة من خدمة الذكاء الاصطناعي إلى الباك إند.
    """
    endpoint = f"{FASTAPI_BACKEND_URL}/proctor_updates/{session_id}"
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": f"Bearer {AI_SERVICE_AUTH_TOKEN}" # لو الـ endpoint بيحتاج مصادقة
    }

    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(update_data))
        response.raise_for_status() # هيرمي استثناء لو حصل أي خطأ في الـ HTTP (مثلاً 404, 500)
        print(f"Update sent successfully for session {session_id}. Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending update for session {session_id}: {e}")
        print(f"Response content: {e.response.text if e.response else 'N/A'}")

def simulate_ai_monitoring(session_id: str):
    """
    دالة لمحاكاة عمل موديل الذكاء الاصطناعي وإرسال الأحداث.
    في تطبيقك الحقيقي، هنا هتكون لوجيك الموديل الحقيقي اللي بيحلل الفيديو/الصوت.
    """
    print(f"\n--- Starting AI monitoring simulation for session: {session_id} ---")
    event_types = ["face_away", "multiple_faces", "suspicious_sound", "browser_tab_change", "person_detection"]
    
    for i in range(10): # محاكاة لـ 10 اكتشافات
        time.sleep(random.uniform(2, 5)) # انتظار عشوائي بين الاكتشافات
        
        # اختيار حدث عشوائي
        event_type = random.choice(event_types)
        risk_delta = random.randint(1, 5) # زيادة عشوائية في درجة المخاطرة

        # بناء البيانات اللي هنبعتها
        update_data = {
            "type": event_type,
            "risk_delta": risk_delta,
            "details": {
                "message": f"Detected {event_type} at {datetime.now().isoformat()}",
                "confidence": round(random.uniform(0.7, 0.99), 2)
            },
            "snapshot_url": f"https://placehold.co/600x400/FF0000/FFFFFF?text={event_type.replace('_', '+')}"
        }
        
        print(f"Simulating event: {event_type} with risk delta {risk_delta}")
        send_proctor_update(session_id, update_data)

if __name__ == "__main__":
    # مثال على استخدام الدالة لمحاكاة المراقبة لجلسة معينة
    # في تطبيقك الحقيقي، الـ session_id ده هييجي من الواجهة الأمامية أو من داتا بيز
    # بعد ما الطالب يبدأ الامتحان.
    test_session_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef" # استبدلها برقم جلسة حقيقي
    
    # تأكد إن الباك إند شغال قبل ما تشغل الكود ده
    simulate_ai_monitoring(test_session_id)
