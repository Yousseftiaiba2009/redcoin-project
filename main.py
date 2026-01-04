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

# العودة للسرعة القديمة لزيادة الصعوبة (ندرة العملة)
MINING_SPEED = 0.0005 

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    # نضمن استعادة رصيدك الضخم الذي جمعته سابقاً
                    return float(data[FOUNDER_ADDR]['balance'])
        except: pass
    return 500000.0

initial_val = load_balance()
START_BALANCE = initial_val # لتتبع ما جنيته منذ تشغيل السيرفر الحالي
wallets = {FOUNDER_ADDR: {"balance": initial_val}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except: pass

def mining_worker():
    global wallets
    while True:
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        # حفظ كل 10 ثوانٍ لضمان الأمان
        if int(time.time()) % 10 == 0:
            save_data()
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    current_bal = wallets[FOUNDER_ADDR]['balance']
    # حساب صافي الربح في الجلسة الحالية
    session_profit = current_bal - START_BALANCE
    return jsonify({
        "balance": round(current_bal, 6),
        "session_profit": round(session_profit, 6)
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
