import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 

# --- الملفات والقواعد ---
DB_FILE = "balance_db.txt"
LOG_FILE = "blockchain_log.json"
WALLETS_FILE = "wallets_db.json"  # الملف الجديد لحفظ المحافظ

# --- إعدادات الحصن للمؤسس ---
START_BALANCE = 500000.0
BASE_TIMESTAMP = 1735568526 
MINING_SPEED = 0.00005
FOUNDER_KEY = "RTC_ADMIN_2025_SECURE"

# --- وظائف إدارة البيانات (الحصن الشامل) ---

def load_all_wallets():
    """تحميل كل المحافظ من الملف عند التشغيل"""
    if os.path.exists(WALLETS_FILE):
        with open(WALLETS_FILE, 'r') as f:
            return json.load(f)
    # إذا لم يوجد الملف، ننشئ محفظة المؤسس فقط
    passed_seconds = time.time() - BASE_TIMESTAMP
    founder_bal = START_BALANCE + (passed_seconds * MINING_SPEED)
    return {
        "RTC-FOUNDER-001": {
            "balance": founder_bal,
            "key": FOUNDER_KEY,
            "type": "Founder"
        }
    }

def save_all_wallets():
    """حفظ كل المحافظ في الملف الدائم"""
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f)

def save_transaction(tx):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: logs = json.load(f)
    logs.append(tx)
    with open(LOG_FILE, 'w') as f: json.dump(logs, f)

# --- تهيئة البيانات ---
wallets = load_all_wallets()
mining_data = {"total": wallets["RTC-FOUNDER-001"]["balance"]}

# --- محرك التعدين المستمر للمؤسس ---
def mining_worker():
    while True:
        mining_data["total"] += MINING_SPEED
        wallets["RTC-FOUNDER-001"]["balance"] = mining_data["total"]
        
        # حفظ الأرصدة كل 30 ثانية لضمان الثبات
        if int(time.time()) % 30 == 0:
            save_all_wallets()
            with open(DB_FILE, "w") as f: f.write(str(mining_data["total"]))
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات البرمجية (API) ---

@app.route('/')
def status():
    return jsonify({
        "coin": "RTC",
        "founder_balance": round(wallets["RTC-FOUNDER-001"]["balance"], 8),
        "total_active_wallets": len(wallets),
        "status": "Secure Database Active"
    })

@app.route('/create_wallet')
def create():
    addr = f"RTC-{str(uuid.uuid4())[:8].upper()}"
    key = str(uuid.uuid4())[:12]
    wallets[addr] = {"balance": 0.0, "key": key, "type": "User"}
    save_all_wallets() # حفظ المحفظة الجديدة فوراً
    return jsonify({"address": addr, "private_key": key})

@app.route('/send')
def send():
    sender = request.args.get('from')
    key = request.args.get('key')
    target = request.args.get('to')
    try:
        amt = float(request.args.get('amount'))
    except: return jsonify({"error": "Wrong amount"})

    if sender in wallets and wallets[sender]['key'] == key:
        if wallets[sender]['balance'] >= amt and target in wallets:
            # تنفيذ الخصم والإضافة
            wallets[sender]['balance'] -= amt
            wallets[target]['balance'] += amt
            
            # تسجيل العملية
            tx = {"from": sender, "to": target, "amount": amt, "time": time.ctime()}
            save_transaction(tx)
            save_all_wallets() # حفظ التغييرات في الأرصدة فوراً
            
            return jsonify({"status": "Success", "details": tx})
        return jsonify({"error": "Balance or Receiver issue"})
    return jsonify({"error": "Auth failed"})

@app.route('/ledger')
def view_ledger():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: return jsonify(json.load(f))
    return jsonify([])

@app.route('/balance/<address>')
def check_balance(address):
    """مسار جديد للتأكد من رصيد أي محفظة"""
    if address in wallets:
        return jsonify({"address": address, "balance": round(wallets[address]['balance'], 8)})
    return jsonify({"error": "Wallet not found"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
