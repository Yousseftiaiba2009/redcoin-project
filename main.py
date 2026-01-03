import time
import threading
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- الإعدادات الأساسية ---
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"
MINING_SPEED = 0.0005 

# متغير لتخزين الرصيد عند لحظة تشغيل السيرفر
START_BALANCE = 0.0

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    return max(float(data[FOUNDER_ADDR]['balance']), 500000.0)
        except:
            pass
    return 500000.0

# ضبط رصيد البداية والرصيد الحالي
initial_val = load_balance()
START_BALANCE = initial_val
wallets = {FOUNDER_ADDR: {"balance": initial_val}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except:
        pass

def mining_worker():
    global wallets
    while True:
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        if int(time.time()) % 10 == 0:
            save_data()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    current_bal = wallets[FOUNDER_ADDR]['balance']
    # حساب ما تم جنينه منذ تشغيل السيرفر
    session_profit = current_bal - START_BALANCE
    
    return jsonify({
        "balance": round(current_bal, 6),
        "session_profit": round(session_profit, 6), # الربح منذ البداية
        "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - (session_profit/MINING_SPEED) if session_profit > 0 else time.time()))
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
