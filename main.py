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

# --- إعدادات السرعة الفائقة (تعديل المؤسس) ---
MINING_SPEED = 11.5       # سرعة البرق: 11.5 عملة في الثانية الواحدة!
NOTIFY_EVERY = 1000.0     # نصيحة: ارفع الإشعار لـ 1000 عملة لأن الـ 100 ستأتيك كل 8 ثوانٍ وتزعجك
SAVE_EVERY_SECONDS = 5    # تقليل وقت الحفظ لـ 5 ثوانٍ للأمان بسبب السرعة العالية

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
                if FOUNDER_ADDR in data:
                    return data[FOUNDER_ADDR]['balance']
        except: pass
    return 500000.0

wallets = {FOUNDER_ADDR: {"balance": load_balance()}}

def save_data():
    try:
        with open(WALLETS_FILE, 'w') as f:
            json.dump(wallets, f)
    except: pass

def mining_worker():
    global wallets
    last_notified_bal = wallets[FOUNDER_ADDR]["balance"]
    
    # رسالة انطلاق تدل على القوة
    send_telegram(f"⚡ *RTC Hyper-Drive Active*\nSpeed: `11.5 RTC/sec`\nTarget: `1,000,000` 🚀")

    while True:
        # زيادة الرصيد
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        current_bal = wallets[FOUNDER_ADDR]["balance"]
        
        # إرسال إشعار تليجرام عند تحقيق الهدف المالي
        if current_bal - last_notified_bal >= NOTIFY_EVERY:
            send_telegram(f"🔥 *Fast Growth Update*\nTotal: `{current_bal:,.2f} RTC`")
            last_notified_bal = current_bal
            save_data() 

        # حفظ دوري مكثف
        if int(time.time()) % SAVE_EVERY_SECONDS == 0:
            save_data()
            
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    return jsonify({"balance": round(wallets[FOUNDER_ADDR]['balance'], 4)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
