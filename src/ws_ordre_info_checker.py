import websocket
import json
import time
import hmac
import base64
import dotenv
import os

dotenv.load_dotenv()

# APIキー情報
api_key = os.getenv("ACCESS")
secret_key = os.getenv("SECRET")
passphrase = os.getenv("PASS")

# WebSocketエンドポイント
ws_endpoint = "wss://ws.bitget.com/v2/ws/private"

def get_sign(timestamp, method, request_path):
    message = str(timestamp) + method + request_path
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)

def on_message(ws, message):
    print(f"受信メッセージ: {message}")
    data = json.loads(message)
    if data.get("event") == "login" and data.get("code") == 0:
        print("ログイン成功。チャンネルを購読します。")
        subscribe_data = {
            "op": "subscribe",
            "args": [{
                "instType": "SPOT",
                "channel": "orders",
                "instId": "BTCUSDT"
            }]
        }
        ws.send(json.dumps(subscribe_data))

def on_error(ws, error):
    print(f"エラー: {error}")

def on_close(ws):
    print("接続が閉じられました")

def on_open(ws):
    timestamp = int(time.time())
    sign = get_sign(timestamp, "GET", "/user/verify")
    
    login_data = {
        "op": "login",
        "args": [{
            "apiKey": api_key,
            "passphrase": passphrase,
            "timestamp": str(timestamp),
            "sign": sign.decode('utf-8')
        }]
    }
    ws.send(json.dumps(login_data))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_endpoint,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
