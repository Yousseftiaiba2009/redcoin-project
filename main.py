import time
import threading
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- إعدادات قاعدة البيانات ---
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"

# السرعة المعتمدة (0.00005) لضمان الندرة
MINING_SPEED = 0.00005 

# متغيرات الجلسة
start_time = time.time()

def load_balance():
    """تحميل الرصيد أو البدء بالرقم المعتمد 793485"""
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return float(data[FOUNDER_ADDR]['balance'])
        except:
            pass
    # القيمة التأسيسية التي طلبتها
    return 793485.0

# تهيئة الرصيد
initial_balance = load_balance()
session_start_balance = initial_balance
wallets = {FOUNDER_ADDR: {"balance": initial_balance}}

def save_data():
    """حفظ البيانات تلقائياً"""
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except:
        pass

def mining_loop():
    """محرك التعدين المستمر"""
    global wallets
    while True:
        # إضافة الزيادة الدقيقة
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ تلقائي كل 20 ثانية
        if int(time.time()) % 20 == 0:
            save_data()
            
        time.sleep(1)

# تشغيل التعدين في الخلفية
threading.Thread(target=mining_loop, daemon=True).start()

@app.route('/founder_data')
def get_founder_data():
    """تغذية الداشبورد بالبيانات"""
    current_balance = wallets[FOUNDER_ADDR]['balance']
    return jsonify({
        "balance": round(current_balance, 8),
        "session_profit": round(current_balance - session_start_balance, 8),
        "hashrate": "0.00 H/s",
        "status": "Connected",
        "uptime": int(time.time() - start_time)
    })

if __name__ == "__main__":
    # التشغيل على بورت 10000 المخصص لـ Render
    app.run(host='0.0.0.0', port=10000)
