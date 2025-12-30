import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)
# تفعيل الـ CORS هو الذي سيجعل المحفظة تتصل وتظهر اللون الأخضر
CORS(app) 

# إعدادات تعدين عملتك RTC
mining_data = {
    "rtc_total_mined": 0.0,
    "mining_speed": 277.77  # سرعة التعدين
}

def start_mining():
    while True:
        mining_data["rtc_total_mined"] += mining_data["mining_speed"]
        time.sleep(1)

# تشغيل التعدين في خلفية السيرفر الألماني
threading.Thread(target=start_mining, daemon=True).start()

@app.route('/')
def get_mining_status():
    return jsonify({
        "coin": "RTC",
        "status": "Mining Active",
        "total_mined": round(mining_data["rtc_total_mined"], 6)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
