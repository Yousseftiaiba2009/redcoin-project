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

# السرعة الاستراتيجية الجديدة (ندرة عالية جداً)
MINING_SPEED = 0.00005 

# متغيرات الجلسة لمراقبة الأداء
start_time = time.time()
session_start_balance = 0.0

def load_balance():
    """تحميل الرصيد مع ضمان قراءة القيمة العشرية بدقة"""
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return float(data[FOUNDER_ADDR]['balance'])
        except:
            pass
    return 500000.0

# تهيئة الرصيد عند التشغيل
initial_balance = load_balance()
session_start_balance = initial_balance
wallets = {FOUNDER_ADDR: {"balance": initial_balance}}

def save_data():
    """حفظ البيانات بدقة عالية في ملف JSON"""
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except:
        pass

def mining_loop():
    """محرك التعدين بالسرعة الجديدة"""
    global wallets
    while True:
        # إضافة الزيادة بالدقة المطلوبة
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ البيانات كل 20 ثانية لضمان استقرار السيرفر ومواكبة التغيرات
        if int(time.time()) % 20 == 0:
            save_data()
            
        time.sleep(1)

# إطلاق محرك التعدين في الخلفية
threading.Thread(target=mining_loop, daemon=True).start()

@app.route('/founder_data')
def get_founder_data():
    """تصدير البيانات بدقة 8 خانات عشرية"""
    current_balance = wallets[FOUNDER_ADDR]['balance']
    # تم تغيير round إلى 8 ليتوافق مع واجهة الداشبورد الجديدة
    return jsonify({
        "balance": round(current_balance, 8),
        "session_profit": round(current_balance - session_start_balance, 8),
        "hashrate": "0.00 H/s",
        "status": "Connected",
        "uptime": int(time.time() - start_time)
    })

if __name__ == "__main__":
    # التشغيل على بورت Render الافتراضي
    app.run(host='0.0.0.0', port=10000)
