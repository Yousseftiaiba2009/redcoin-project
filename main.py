import time
import threading
import os
import json
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- إعدادات مركز القيادة ---
TELEGRAM_TOKEN = "8167725310:AAHLU3KwHsDBjKWTgHG_W3ZbtqiH0qoUrK8"
CHAT_ID = "7058513615"
WALLETS_FILE = "wallets_db.json"
FOUNDER_ADDR = "RTC-FOUNDER-001"

# السرعة الهادئة والمستقرة التي اخترتها
MINING_SPEED = 0.0005 

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def load_balance():
    # استعادة الرصيد الحقيقي من قاعدة البيانات لضمان عدم ضياع الأرباح السابقة
    if os.path.exists(WALLETS_FILE):
        try:
            with open(WALLETS_FILE, 'r') as f:
                data = json.load(f)
                if FOUNDER_ADDR in data:
                    bal = data[FOUNDER_ADDR]['balance']
                    # التأكد من أن الرصيد لا يقل عن نصف مليون أبداً
                    return max(bal, 500000.0)
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
    # إشعار واحد فقط عند التشغيل للتأكيد على حالة الشبكة
    initial_bal = wallets[FOUNDER_ADDR]["balance"]
    send_telegram(f"🔋 *RTC Network Online*\nFounder Balance Restored: `{initial_bal:,.4f} RTC`\nMining Speed: `0.0005/s`")

    while True:
        # زيادة الرصيد الحقيقي بالسرعة الجديدة
        wallets[FOUNDER_ADDR]["balance"] += MINING_SPEED
        
        # حفظ البيانات بصمت كل 10 ثوانٍ دون إرسال إشعارات
        if int(time.time()) % 10 == 0:
            save_data()
            
        time.sleep(1)

threading.Thread(target=mining_worker, daemon=True).start()

@app.route('/founder_data')
def founder_data():
    # إرسال الرصيد بدقة 6 خانات للمحفظة
    return jsonify({"balance": round(wallets[FOUNDER_ADDR]['balance'], 6)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
