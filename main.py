import time
import threading
from flask import Flask
import os

app = Flask(__name__)

# متغيرات عملة RTC
rtc_total_mined = 0
mining_speed = 0.0001  # سرعة التعدين لكل ثانية

def mine_rtc():
    global rtc_total_mined
    while True:
        # هنا تتم عملية "التعدين" الحسابية الخاصة بعملتك
        rtc_total_mined += mining_speed
        time.sleep(1) # السيرفر يعمل كل ثانية لزيادة الرصيد

# تشغيل التعدين في الخلفية
threading.Thread(target=mine_rtc, daemon=True).start()

@app.route('/')
def status():
    return {
        "coin": "RTC",
        "status": "Mining Active",
        "total_mined": round(rtc_total_mined, 6),
        "server": "Germany-Render"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
