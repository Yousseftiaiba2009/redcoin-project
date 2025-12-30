import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
# تفعيل CORS ضروري للسماح لموقعك الخارجي بالاتصال بالسيرفر
CORS(app) 

# --- إعدادات الملفات ---
WALLETS_FILE = "wallets_db.json"
LOG_FILE = "blockchain_log.json"

# --- إعدادات المؤسس ---
START_BALANCE = 500000.0
BASE_TIMESTAMP = 1735568526 
MINING_SPEED = 0.00005
FOUNDER_KEY = "RTC_ADMIN_2025_SECURE"

# --- وظائف إدارة البيانات ---

def load_all_wallets():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # حالة عدم وجود ملف: إنشاء محفظة المؤسس
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

def save_transaction(tx):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f: logs = json.load(f)
        except: pass
    logs.append(tx)
    with open(LOG_FILE, 'w') as f: json.dump(logs, f)

# تهيئة البيانات عند التشغيل
wallets = load_all_wallets()

# --- محرك التعدين المستمر للمؤسس ---
def mining_worker():
    while True:
        wallets["RTC-FOUNDER-001"]["balance"] += MINING_SPEED
        # حفظ البيانات كل 60 ثانية لضمان ثباتها على Render
        if int(time.time()) % 60 == 0:
            save_all_wallets()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات البرمجية (API) ---

@app.route('/')
def status():
    return jsonify({
        "coin": "RTC",
        "founder_balance": round(wallets["RTC-FOUNDER-001"]["balance"], 8),
        "total_wallets": len(wallets),
        "status": "Online"
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400
    
    key_input = data.get('private_key')
    for addr, details in wallets.items():
        if details.get('key') == key_input:
            return jsonify({
                "status": "success",
                "address": addr,
                "balance": round(details['balance'], 8)
            })
    return jsonify({"error": "Invalid Key"}), 401

@app.route('/create_wallet')
def create():
    addr = f"RTC-{str(uuid.uuid4())[:8].upper()}"
    key = str(uuid.uuid4())[:12]
    wallets[addr] = {"balance": 0.0, "key": key, "type": "User"}
    save_all_wallets()
    return jsonify({"address": addr, "private_key": key})

@app.route('/balance/<address>')
def check_balance(address):
    if address in wallets:
        return jsonify({"address": address, "balance": round(wallets[address]['balance'], 8)})
    return jsonify({"error": "Not found"}), 404

@app.route('/send')
def send():
    sender = request.args.get('from')
    key = request.args.get('key')
    target = request.args.get('to')
    try:
        amt = float(request.args.get('amount'))
    except: return jsonify({"error": "الكمية غير صحيحة"})

    if sender in wallets and wallets[sender]['key'] == key:
        if wallets[sender]['balance'] >= amt and target in wallets:
            wallets[sender]['balance'] -= amt
            wallets[target]['balance'] += amt
            
            tx = {"from": sender, "to": target, "amount": amt, "time": time.ctime()}
            save_transaction(tx)
            save_all_wallets()
            return jsonify({"status": "Success", "details": tx})
        return jsonify({"error": "رصيد غير كافٍ أو مستلم غير موجود"})
    return jsonify({"error": "فشل المصادقة"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
