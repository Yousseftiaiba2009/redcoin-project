import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
# تفعيل CORS للسماح لموقعك على InfinityFree بالاتصال بالسيرفر
CORS(app, resources={ seminar: {"origins": "*"}}) 

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
    """تحميل الأرصدة والمحافظ من الذاكرة الدائمة"""
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # حساب رصيد المؤسس بناءً على الوقت المنقضي منذ الانطلاق
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
    """حفظ البيانات فوراً لمنع الضياع"""
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f)

def save_transaction(tx):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: logs = json.load(f)
    logs.append(tx)
    with open(LOG_FILE, 'w') as f: json.dump(logs, f)

# تهيئة البيانات عند التشغيل
wallets = load_all_wallets()

# --- محرك التعدين (تعدين المؤسس المستمر) ---
def mining_worker():
    while True:
        # إضافة العملات لمحفظة المؤسس كل ثانية
        wallets["RTC-FOUNDER-001"]["balance"] += MINING_SPEED
        
        # حفظ تلقائي كل دقيقة لضمان ثبات البيانات على Render
        if int(time.time()) % 60 == 0:
            save_all_wallets()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات البرمجية (API) ---

@app.route('/')
def status():
    """الحالة العامة للشبكة"""
    return jsonify({
        "coin": "RTC",
        "founder_balance": round(wallets["RTC-FOUNDER-001"]["balance"], 8),
        "total_wallets": len(wallets),
        "status": "Online"
    })

@app.route('/login', methods=['POST'])
def login():
    """نظام تسجيل الدخول بالمفتاح الخاص"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    key_input = data.get('private_key')
    
    # البحث عن المحفظة المرتبطة بالمفتاح
    for addr, details in wallets.items():
        if details.get('key') == key_input:
            return jsonify({
                "status": "success",
                "address": addr,
                "balance": round(details['balance'], 8),
                "type": details['type']
            })
    
    return jsonify({"error": "Invalid Private Key"}), 401

@app.route('/create_wallet')
def create():
    """إنشاء محفظة جديدة وحفظها"""
    addr = f"RTC-{str(uuid.uuid4())[:8].upper()}"
    key = str(uuid.uuid4())[:12]
    wallets[addr] = {"balance": 0.0, "key": key, "type": "User"}
    save_all_wallets()
    return jsonify({"address": addr, "private_key": key})

@app.route('/balance/<address>')
def check_balance(address):
    """الاستعلام عن رصيد أي محفظة"""
    if address in wallets:
        return jsonify({
            "address": address, 
            "balance": round(wallets[address]['balance'], 8)
        })
    return jsonify({"error": "Wallet not found"}), 404

@app.route('/send')
def send():
    """نظام تحويل العملات الآمن"""
    sender = request.args.get('from')
    key = request.args.get('key')
    target = request.args.get('to')
    try:
        amt = float(request.args.get('amount'))
    except: return jsonify({"error": "Invalid amount"})

    if sender in wallets and wallets[sender]['key'] == key:
        if wallets[sender]['balance'] >= amt and target in wallets:
            wallets[sender]['balance'] -= amt
            wallets[target]['balance'] += amt
            
            tx = {"from": sender, "to": target, "amount": amt, "time": time.ctime()}
            save_transaction(tx)
            save_all_wallets()
            return jsonify({"status": "Success", "details": tx})
        return jsonify({"error": "Insufficient balance or invalid target"})
    return jsonify({"error": "Authentication failed"})

if __name__ == "__main__":
    # تشغيل السيرفر على المنفذ المطلوب لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
# تفعيل CORS ضروري جداً لعمل الأزرار من موقعك الخارجي
CORS(app) 

# --- الملفات ---
WALLETS_FILE = "wallets_db.json"
LOG_FILE = "blockchain_log.json"

# --- إعدادات المؤسس ---
START_BALANCE = 500000.0
BASE_TIMESTAMP = 1735568526 
MINING_SPEED = 0.00005
FOUNDER_KEY = "RTC_ADMIN_2025_SECURE"

def load_all_wallets():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f: return json.load(f)
        except: pass
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

wallets = load_all_wallets()

def mining_worker():
    while True:
        wallets["RTC-FOUNDER-001"]["balance"] += MINING_SPEED
        if int(time.time()) % 60 == 0:
            save_all_wallets()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات (Routes) ---

@app.route('/')
def status():
    return jsonify({
        "founder_balance": round(wallets["RTC-FOUNDER-001"]["balance"], 8),
        "total_wallets": len(wallets)
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    key_input = data.get('private_key')
    for addr, details in wallets.items():
        if details.get('key') == key_input:
            return jsonify({"status": "success", "address": addr, "balance": details['balance']})
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

# هذا هو الجزء الذي كان ينقصك لتفعيل الإرسال
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
        return jsonify({"error": "الرصيد غير كافٍ أو العنوان خطأ"})
    return jsonify({"error": "فشل التحقق من الهوية"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
