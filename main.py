import websocket
import json
import threading
import time
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

app = Flask('')
@app.route('/')
def home():
    return "Onliner is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    from threading import Thread
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

def send_heartbeat(ws, interval):
    while True:
        time.sleep(interval)
        ws.send(json.dumps({"op": 1, "d": None}))

def on_open(ws):
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Linux",
                "$browser": "Discord Client",
                "$release_channel": "stable",
                "$client_build_number": 117300,
                "$client_event_source": None
            },
            "presence": {
                "status": "idle",
                "afk": False
            }
        }
    }
    ws.send(json.dumps(auth))

def on_message(ws, message):
    data = json.loads(message)
    if data.get('op') == 10:
        interval = data['d']['heartbeat_interval'] / 1000
        threading.Thread(target=send_heartbeat, args=(ws, interval), daemon=True).start()
    if data.get('t') == "READY":
        print(f"Logged in as {data['d']['user']['username']}")

ws = websocket.WebSocketApp("wss://gateway.discord.gg/?v=9&encoding=json",
                            on_open=on_open,
                            on_message=on_message)

if __name__ == "__main__":
    keep_alive()
    ws.run_forever()
