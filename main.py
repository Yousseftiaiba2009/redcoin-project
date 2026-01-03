import time
import threading
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- إعدادات مركز القيادة ---
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"
MINING_SPEED = 0.0005  # السرعة القديمة الرصينة (تعدين صعب)

# متغير لحساب ما تم جنيه منذ تشغيل السيرفر الحالي
START_SESSION_BALANCE = 0.0

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return float(data[FOUNDER_ADDR]['balance'])
        except: pass
    return 500000.0 # الرصيد التأسيسي للمؤسس

# تهيئة البيانات عند انطلاق السيرفر
initial_balance = load_balance()
START_SESSION_BALANCE = initial_balance
wallets = {FOUNDER_ADDR: {"balance": initial_balance}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except: pass

def mining_worker():
    global wallets
    while True:
        # عملية التعدين المستمرة
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ البيانات في ملف JSON كل 15 ثانية صمتاً
        if int(time.time()) % 15 == 0:
            save_data()
        time.sleep(1)

# تشغيل خيط التعدين في الخلفية
threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    current_bal = wallets[FOUNDER_ADDR]['balance']
    return jsonify({
        "balance": round(current_bal, 6),
        "session_profit": round(current_bal - START_SESSION_BALANCE, 6),
        "status": "online"
    })

if __name__ == "__main__":
    # تشغيل السيرفر على البورت المخصص لـ Render
    app.run(host='0.0.0.0', port=10000)
