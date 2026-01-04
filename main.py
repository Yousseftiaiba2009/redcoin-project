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
MINING_SPEED = 0.00005 

start_time = time.time()

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                return float(data[FOUNDER_ADDR]['balance'])
        except: pass
    # تم تثبيت الرقم الجديد بناءً على طلبك
    return 793485.0 

initial_balance = load_balance()
session_start_balance = initial_balance
wallets = {FOUNDER_ADDR: {"balance": initial_balance}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except: pass

def mining_loop():
    global wallets
    while True:
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        if int(time.time()) % 15 == 0:
            save_data()
        time.sleep(1)

threading.Thread(target=mining_loop, daemon=True).start()

@app.route('/founder_data')
def get_founder_data():
    current_balance = wallets[FOUNDER_ADDR]['balance']
    return jsonify({
        "balance": float(f"{current_balance:.8f}"),
        "session_profit": float(f"{(current_balance - session_start_balance):.8f}"),
        "hashrate": "0.00 H/s",
        "status": "Secure-Mining"
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
