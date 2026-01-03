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

# السرعة التي اعتمدناها (0.0005) لضمان صعوبة التعدين وندرة العملة
MINING_SPEED = 0.00005 

# متغيرات الجلسة لمراقبة الأداء منذ التشغيل
start_time = time.time()
session_start_balance = 0.0

def load_balance():
    """تحميل الرصيد من الملف أو البدء برصيد المؤسس"""
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return float(data[FOUNDER_ADDR]['balance'])
        except:
            pass
    return 500000.0

# تهيئة الرصيد
initial_balance = load_balance()
session_start_balance = initial_balance
wallets = {FOUNDER_ADDR: {"balance": initial_balance}}

def save_data():
    """حفظ البيانات في ملف JSON"""
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except:
        pass

def mining_loop():
    """المحرك الرئيسي لعملية التعدين"""
    global wallets
    while True:
        # إضافة الزيادة الدقيقة للرصيد
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ تلقائي كل 20 ثانية لضمان استقرار السيرفر
        if int(time.time()) % 20 == 0:
            save_data()
            
        time.sleep(1)

# تشغيل التعدين في خلفية السيرفر
threading.Thread(target=mining_loop, daemon=True).start()

@app.route('/founder_data')
def get_founder_data():
    """نقطة النهاية (API) التي تغذي الداشبورد بالبيانات"""
    current_balance = wallets[FOUNDER_ADDR]['balance']
    return jsonify({
        "balance": round(current_balance, 6),
        "session_profit": round(current_balance - session_start_balance, 6),
        "hashrate": "0.00 H/s",  # تظهر في الواجهة كما في الصورة
        "status": "Connected",   # حالة الاتصال للواجهة
        "uptime": int(time.time() - start_time)
    })

if __name__ == "__main__":
    # التشغيل على المنفذ الافتراضي لخدمات الاستضافة السحابية
    app.run(host='0.0.0.0', port=10000)
