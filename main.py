import time
import threading
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- إعدادات الملفات ---
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"
DEFAULT_START = 500000.0  # الرصيد الافتراضي فقط إذا كان السيرفر جديداً كلياً
MINING_SPEED = 0.05       # سرعة التعدين الصاروخية للمليون

# --- وظيفة جلب الرصيد الحقيقي من السيرفر ---
def get_current_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return data[FOUNDER_ADDR]['balance']
        except:
            pass
    return DEFAULT_START

# تهيئة الرصيد من السيرفر مباشرة عند التشغيل
current_balance = get_current_balance()

wallets = {
    FOUNDER_ADDR: {
        "balance": current_balance,
        "key": "RTC_ADMIN_2025_SECURE",
        "type": "Founder"
    }
}

# --- وظيفة حفظ البيانات الدورية ---
def save_data():
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f)

# --- محرك التعدين ---
def mining_worker():
    global wallets
    while True:
        # الزيادة تحدث على الرقم المستلم من السيرفر
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ كل 10 ثواني لضمان عدم ضياع أي كسر من العملة
        if int(time.time()) % 10 == 0:
            save_data()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    return jsonify({
        "balance": round(wallets[FOUNDER_ADDR]['balance'], 4),
        "status": "Syncing from Server"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
