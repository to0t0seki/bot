import time
import hmac
import base64
import requests
import json
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
load_dotenv()

# APIキーの設定
API_KEY = os.getenv("SUB_KEY")
SECRET_KEY = os.getenv("SUB_SECRET")
PASSPHRASE = os.getenv("SUB_PASS")

# APIのエンドポイント
BASE_URL = "https://api.bitget.com"
ENDPOINT = "/api/v2/spot/trade/place-order"

# オーダーの詳細
symbol = "BTCUSDT"
side = "buy"
order_type = "limit"
force = "gtc"
price = "95000"
size = "0.0001"
client_oid = str(int(time.time() * 1000))  # ミリ秒単位のタイムスタンプをclient_oidとして使用

# リクエストボディの作成
body = {
    "symbol": symbol,
    "side": side,
    "orderType": order_type,
    "force": force,
    "price": price,
    "size": size,
    "clientOid": client_oid
}

# タイムスタンプの生成
timestamp = str(int(time.time() * 1000))

# 署名の生成
message = timestamp + "POST" + ENDPOINT + json.dumps(body)
signature = base64.b64encode(hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), digestmod='sha256').digest()).decode('utf-8')

# ヘッダーの設定
headers = {
    "ACCESS-KEY": API_KEY,
    "ACCESS-SIGN": signature,
    "ACCESS-TIMESTAMP": timestamp,
    "ACCESS-PASSPHRASE": PASSPHRASE,
    "Content-Type": "application/json",
    "locale": "ja-JP"
}

# リクエストの送信とエラーハンドリング
try:
    response = requests.post(BASE_URL + ENDPOINT, headers=headers, data=json.dumps(body), timeout=10)
    response.raise_for_status()  # HTTPエラーが発生した場合に例外をスロー
    print("オーダーが正常に発注されました:", response.json())
except requests.exceptions.ConnectionError as ce:
    print("接続エラーが発生しました:", ce)
except requests.exceptions.Timeout as te:
    print("リクエストがタイムアウトしました:", te)
except requests.exceptions.HTTPError as he:
    print("HTTPエラーが発生しました:", he)
    if response.status_code == 400:
        error_data = response.json()
        print("エラーコード:", error_data.get('code'))
        print("エラーメッセージ:", error_data.get('msg'))
except requests.exceptions.RequestException as re:
    print("リクエストエラーが発生しました:", re)
except Exception as e:
    print("予期せぬエラーが発生しました:", e)
