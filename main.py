import time
import threading
import uuid
import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 

# --- إعدادات حصن المؤسس ---
START_BALANCE = 500000.0
BASE_TIMESTAMP = 1735568526 
MINING_SPEED = 0.00005
DB_FILE = "balance_db.txt"
LOG_FILE = "blockchain_log.json"

# مفتاح الأمان الخاص بك (لا تعطِه لأحد)
FOUNDER_KEY = "RTC_ADMIN_2025_SECURE" 

# --- نظام المحافظ (قاعدة بيانات أولية) ---
wallets = {
    "RTC-FOUNDER-001": {
        "balance": START_BALANCE,
        "key": FOUNDER_KEY,
        "type": "Founder"
    }
}

# --- إدارة سجل العمليات (Ledger) ---
def save_transaction(tx):
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: logs = json.load(f)
    logs.append(tx)
    with open(LOG_FILE, 'w') as f: json.dump(logs, f)

# --- محرك التعدين المستقر ---
def load_initial():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return float(f.read().strip())
        except: pass
    return START_BALANCE + ((time.time() - BASE_TIMESTAMP) * MINING_SPEED)

mining_data = {"total": load_initial()}

def mining_worker():
    while True:
        mining_data["total"] += MINING_SPEED
        wallets["RTC-FOUNDER-001"]["balance"] = mining_data["total"]
        if int(time.time()) % 30 == 0:
            with open(DB_FILE, "w") as f: f.write(str(mining_data["total"]))
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

# --- المسارات البرمجية ---

@app.route('/')
def status():
    return jsonify({
        "coin": "RTC",
        "founder_balance": round(mining_data["total"], 8),
        "status": "Secure Blockchain Active"
    })

@app.route('/create_wallet')
def create():
    addr = f"RTC-{str(uuid.uuid4())[:8].upper()}"
    key = str(uuid.uuid4())[:12]
    wallets[addr] = {"balance": 0.0, "key": key, "type": "User"}
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
            wallets[sender]['balance'] -= amt
            wallets[target]['balance'] += amt
            tx = {"from": sender, "to": target, "amount": amt, "time": time.ctime()}
            save_transaction(tx)
            return jsonify({"status": "Success", "details": tx})
        return jsonify({"error": "Balance or Receiver issue"})
    return jsonify({"error": "Auth failed"})

@app.route('/ledger')
def view_ledger():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
