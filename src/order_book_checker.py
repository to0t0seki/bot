import websocket
import json
import time

def on_message(ws, message):
    data = json.loads(message)
    if 'data' in data:
        print("オーダーブック更新:")
        for item in data['data']:
            print(f"Asks: {item['asks']}")
            print(f"Bids: {item['bids']}")
            print(f"Timestamp: {item['ts']}")
            print("---")

def on_error(ws, error):
    print(f"エラーが発生しました: {error}")

def on_close(ws):
    print("WebSocket接続が閉じられました")

def on_open(ws):
    print("WebSocket接続が開かれました")
    
    # オーダーブックチャンネルの購読
    subscribe_message = {
        "op": "subscribe",
        "args": [
            {
                "instType": "SPOT",
                "channel": "books5",
                "instId": "BTCUSDT"
            }
        ]
    }
    subscribe_message2 = {
    "op": "subscribe",
    "args": [
        {
            "instType": "SPOT",
            "channel": "fill",
            "instId": "default"
        }
    ]
}
    ws.send(json.dumps(subscribe_message2))

def keep_alive(ws):
    while True:
        time.sleep(30)
        ws.send("ping")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.bitget.com/v2/ws/public",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open)

    import threading
    keep_alive_thread = threading.Thread(target=keep_alive, args=(ws,))
    keep_alive_thread.start()

    ws.run_forever()

