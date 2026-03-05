import websocket
import json
import threading
import time
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
tokens = {
    "idle": os.getenv("TOKEN1"),
    "online": os.getenv("TOKEN2")
}

app = Flask('')
@app.route('/')
def home():
    return "Onliner is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

def send_heartbeat(ws, interval):
    while True:
        time.sleep(interval)
        try:
            ws.send(json.dumps({"op": 1, "d": None}))
        except:
            break

def on_message(ws, message):
    data = json.loads(message)
    if data.get('op') == 10:
        interval = data['d']['heartbeat_interval'] / 1000
        threading.Thread(target=send_heartbeat, args=(ws, interval), daemon=True).start()
    if data.get('t') == "READY":
        print(f"Logged in: {data['d']['user']['username']}")

def create_ws(token, status):
    def on_open(ws):
        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "Linux",
                    "$browser": "Discord Client",
                    "$device": "discord.py"
                },
                "presence": {
                    "status": status,
                    "afk": False
                }
            }
        }
        ws.send(json.dumps(auth))

    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json",
                                on_open=on_open,
                                on_message=on_message)
    ws.run_forever()

if __name__ == "__main__":
    keep_alive()

    t1 = threading.Thread(target=create_ws, args=(tokens["idle"], "idle"))

    t2 = threading.Thread(target=create_ws, args=(tokens["online"], "online"))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
