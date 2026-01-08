import time
import threading
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"
# السرعة المعتمدة
MINING_SPEED = 0.00005 

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                return float(data[FOUNDER_ADDR]['balance'])
        except: pass
    # رقمك المعتمد
    return 793485.0

# تهيئة الرصيد في الذاكرة
wallets = {FOUNDER_ADDR: {"balance": load_balance()}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except: pass

def mining_loop():
    while True:
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        if int(time.time()) % 15 == 0:
            save_data()
        time.sleep(1)

# تشغيل التعدين في الخلفية
threading.Thread(target=mining_loop, daemon=True).start()

@app.route('/')
def home():
    return "RTC Server is Running!"

@app.route('/founder_data')
def get_founder_data():
    return jsonify({
        "balance": wallets[FOUNDER_ADDR]['balance'],
        "status": "Connected"
    })

if __name__ == "__main__":
    # هذا التعديل يضمن أن السيرفر يفتح البورت الصحيح تلقائياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
@app.route('/send_crypto/<sender>/<receiver>/<amount>', methods=['POST'])
def send_crypto(sender, receiver, amount):
    try:
        amount = float(amount)
        if sender in wallets and wallets[sender]['balance'] >= amount:
            if receiver not in wallets:
                wallets[receiver] = {"balance": 0.0}
            
            wallets[sender]['balance'] -= amount
            wallets[receiver]['balance'] += amount
            save_data()
            return jsonify({"status": "success", "message": "تم التحويل بنجاح"})
        return jsonify({"status": "error", "message": "رصيد غير كافٍ"})
    except:
        return jsonify({"status": "error", "message": "خطأ في العملية"})
