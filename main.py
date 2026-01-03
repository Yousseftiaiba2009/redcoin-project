import time
import threading
import os
import json
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- البيانات المستخرجة من صورك (مركز القيادة) ---
TELEGRAM_TOKEN = "8167725310:AAHLU3KwHsDBjKWTgHG_W3ZbtqiH0qoUrK8"
CHAT_ID = "7058513615"
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"

# --- إعدادات السرعة والإشعارات (تعديل المؤسس) ---
MINING_SPEED = 11.5        # السرعة الجديدة: 30 عملة في الدقيقة
NOTIFY_EVERY = 100.0      # تحديث التليجرام كل 100 عملة كما طلبت
SAVE_EVERY_SECONDS = 10   # حفظ البيانات كل 10 ثوانٍ لضمان الأمان

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
    return 500000.0 # الرصيد الافتراضي للمؤسس

wallets = {FOUNDER_ADDR: {"balance": load_balance()}}

def save_data():
    with open(WALLETS_FILE, 'w') as f:
        json.dump(wallets, f)

def mining_worker():
    global wallets
    last_saved_bal = wallets[FOUNDER_ADDR]["balance"]
    last_notified_bal = wallets[FOUNDER_ADDR]["balance"]
    
    send_telegram(f"🚀 *Redcoin RTC Turbo Active*\nStarting at: `{last_saved_bal:,.2f}`\nSpeed: `0.5/sec` (30/min)")

    while True:
        # زيادة الرصيد
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        current_bal = wallets[FOUNDER_ADDR]["balance"]
        
        # 1. إرسال إشعار تليجرام كل 100 عملة (طلبك الجديد)
        if current_bal - last_notified_bal >= NOTIFY_EVERY:
            send_telegram(f"📈 *RTC Milestone: +100*\nTotal: `{current_bal:,.2f} RTC`")
            last_notified_bal = current_bal
            save_data() # حفظ تلقائي مع كل إشعار

        # 2. حفظ دوري في الملف كل 10 ثوانٍ للأمان الإضافي
        if int(time.time()) % SAVE_EVERY_SECONDS == 0:
            save_data()
            
        time.sleep(1)

# تشغيل محرك التعدين في الخلفية
threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    return jsonify({"balance": round(wallets[FOUNDER_ADDR]['balance'], 4)})

if __name__ == "__main__":
    # تشغيل السيرفر على بورت 10000 (مناسب لـ Render)
    app.run(host='0.0.0.0', port=10000)
