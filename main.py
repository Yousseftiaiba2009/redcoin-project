import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
# تفعيل CORS الشامل للسماح للمحفظة على GitHub بالوصول للبيانات
CORS(app, resources={r"/*": {"origins": "*"}}) 

# --- إعدادات الملفات ---
WALLETS_FILE = "wallets_db.json"
LOG_FILE = "blockchain_log.json"

# --- إعدادات المؤسس (قمت بتسريعها هنا) ---
START_BALANCE = 500000.0
# سرعة التعدين: 0.00125 تعني زيادة ملحوظة في كل ثانية
MINING_SPEED = 0.05
FOUNDER_KEY = "RTC_ADMIN_2025_SECURE"

# --- وظائف إدارة البيانات ---

def load_all_wallets():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # إنشاء محفظة المؤسس الافتراضية إذا كان الملف غير موجود
    return {
        "RTC-FOUNDER-001": {
            "balance": START_BALANCE,
            "key": FOUNDER_KEY,
            "type": "Founder"
        }
    }

def save_all_wallets():
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f)

# تهيئة البيانات
wallets = load_all_wallets()

# --- محرك التعدين المستمر ---
def mining_worker():
    while True:
        # تعدين الرصيد للمؤسس
        wallets["RTC-FOUNDER-001"]["balance"] += MINING_SPEED
        
        # حفظ البيانات دورياً كل دقيقة (للحفاظ على موارد Render)
        current_time = int(time.time())
        if current_time % 60 == 0:
            save_all_wallets()
            
        time.sleep(1) # نبض السيرفر (تحديث كل ثانية)

# تشغيل محرك التعدين في الخلفية
threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات البرمجية (API) ---

@app.route('/')
def status():
    # هذا المسار سيعرض رصيدك المحدث فوراً عند فتحه
    return jsonify({
        "coin": "Redcoin (RTC)",
        "founder_balance": round(wallets["RTC-FOUNDER-001"]["balance"], 4),
        "total_miners": len(wallets),
        "status": "Network Live",
        "speed_per_sec": MINING_SPEED
    })

@app.route('/balance/<address>')
def check_balance(address):
    # مسار أساسي تستخدمه المحفظة لتحديث رصيدك في الواجهة
    if address in wallets:
        return jsonify({
            "address": address, 
            "balance": round(wallets[address]['balance'], 6)
        })
    return jsonify({"error": "Wallet Not Found"}), 404

# مسار خاص للسماح للمحفظة بجلب رصيد المؤسس مباشرة
@app.route('/founder_data')
def founder_data():
    return jsonify({
        "balance": round(wallets["RTC-FOUNDER-001"]["balance"], 4)
    })

if __name__ == "__main__":
    # الحصول على المنفذ من Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
