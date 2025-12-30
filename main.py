import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)
CORS(app) 

# إعدادات العملة
START_BALANCE = 500000.0
# تاريخ إطلاق العملة الحقيقي (Timestamp) - هذا يمنع التصفير
# سنستخدم هذا الرقم كـ "احتياطي وقت" في حال ضاع ملف balance_db.txt
BASE_TIMESTAMP = 1735568526 

DB_FILE = "balance_db.txt"

def load_balance():
    # أولاً: محاولة القراءة من الملف
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return float(content)
        except:
            pass
    
    # ثانياً: إذا ضاع الملف (بسبب ريندر)، نحسب الرصيد بناءً على الوقت المار
    # لكي لا يبدأ المستخدم من الصفر أبداً
    passed_seconds = time.time() - BASE_TIMESTAMP
    return START_BALANCE + (passed_seconds * 0.00005)

def save_balance(val):
    try:
        with open(DB_FILE, "w") as f:
            f.write(str(val))
    except:
        pass

mining_data = {
    "rtc_total_mined": load_balance(),
    "mining_speed": 0.00005 
}

def start_mining():
    save_counter = 0
    while True:
        mining_data["rtc_total_mined"] += mining_data["mining_speed"]
        
        # حفظ الرصيد في الملف كل 30 ثانية
        save_counter += 1
        if save_counter >= 30:
            save_balance(mining_data["rtc_total_mined"])
            save_counter = 0
            
        time.sleep(1)

# تشغيل التعدين في الخلفية
threading.Thread(target=start_mining, daemon=True).start()

@app.route('/')
def get_mining_status():
    # الحفظ عند زيارة الرابط لضمان عدم ضياع أي لحظة
    save_balance(mining_data["rtc_total_mined"])
    return jsonify({
        "coin": "RTC",
        "status": "Mining Active",
        "total_mined": round(mining_data["rtc_total_mined"], 8),
        "speed": mining_data["mining_speed"],
        "founder": "Satoshi RTC"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
