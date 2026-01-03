import time
import threading
import os
import json
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- البيانات المستخرجة من صورك ---
TELEGRAM_TOKEN = "8167725310:AAHLU3KwHsDBjKWTgHG_W3ZbtqiH0qoUrK8"
CHAT_ID = "7058513615"
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"
MINING_SPEED = 0.05 

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def load_balance():
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                return data[FOUNDER_ADDR]['balance']
        except: pass
    return 500000.0 # نقطة البداية للمؤسس

wallets = {FOUNDER_ADDR: {"balance": load_balance()}}

def mining_worker():
    global wallets
    last_saved_bal = wallets[FOUNDER_ADDR]["balance"]
    send_telegram(f"🚀 *Redcoin RTC Node Started*\nBalance: `{last_saved_bal:,.2f}`")

    while True:
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        # حفظ وإرسال إشعار كل 500 عملة
        if wallets[FOUNDER_ADDR]["balance"] - last_saved_bal >= 500:
            last_saved_bal = wallets[FOUNDER_ADDR]["balance"]
            with open(WALLETS_FILE, 'w') as f:
                json.dump(wallets, f)
            send_telegram(f"💰 *RTC Milestone Reached!*\nCurrent: `{last_saved_bal:,.2f} RTC`")
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    return jsonify({"balance": round(wallets[FOUNDER_ADDR]['balance'], 4)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
