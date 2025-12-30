import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)
CORS(app) 

# اسم ملف قاعدة البيانات البسيطة
DB_FILE = "balance_db.txt"

# دالة لقراءة الرصيد المحفوظ
def load_balance():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return float(f.read())
        except:
            return 500000.0  # في حال وجود خطأ في الملف
    return 500000.0  # القيمة التي حددتها (نصف مليون)

# دالة لحفظ الرصيد في الملف
def save_balance(val):
    with open(DB_FILE, "w") as f:
        f.write(str(val))

# إعدادات التعدين
mining_data = {
    "rtc_total_mined": load_balance(),
    "mining_speed": 0.00005  # السرعة الجديدة المطلوبة
}

def start_mining():
    while True:
        mining_data["rtc_total_mined"] += mining_data["mining_speed"]
        # حفظ الرصيد في الملف لضمان عدم ضياعه عند إعادة التشغيل
        save_balance(mining_data["rtc_total_mined"])
        time.sleep(1)

# تشغيل التعدين في الخلفية
threading.Thread(target=start_mining, daemon=True).start()

@app.route('/')
def get_mining_status():
    return jsonify({
        "coin": "RTC",
        "status": "Mining Active",
        "total_mined": round(mining_data["rtc_total_mined"], 6),
        "speed": mining_data["mining_speed"]
    })

if __name__ == "__main__":
    # Render يستخدم PORT بيئي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
