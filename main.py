import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)
CORS(app) 

DB_FILE = "balance_db.txt"

def load_balance():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                content = f.read().strip()
                return float(content) if content else 500000.0
        except:
            return 500000.0
    return 500000.0

def save_balance(val):
    with open(DB_FILE, "w") as f:
        f.write(str(val))

mining_data = {
    "rtc_total_mined": load_balance(),
    "mining_speed": 0.00005 
}

def start_mining():
    save_counter = 0
    while True:
        mining_data["rtc_total_mined"] += mining_data["mining_speed"]
        
        # حفظ الرصيد في الملف كل 60 ثانية لتقليل الضغط على السيرفر
        save_counter += 1
        if save_counter >= 60:
            save_balance(mining_data["rtc_total_mined"])
            save_counter = 0
            
        time.sleep(1)

# تشغيل التعدين في الخلفية
threading.Thread(target=start_mining, daemon=True).start()

@app.route('/')
def get_mining_status():
    # حفظ فوري عند زيارة الرابط (أو زيارة الكرون جوب) لضمان الدقة
    save_balance(mining_data["rtc_total_mined"])
    return jsonify({
        "coin": "RTC",
        "status": "Mining Active",
        "total_mined": round(mining_data["rtc_total_mined"], 8), # زيادة الدقة لـ 8 أرقام
        "speed": mining_data["mining_speed"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
