import time
import hmac
import base64
import requests
import json

# APIキーの設定
API_KEY = "あなたのAPIキー"
SECRET_KEY = "あなたのシークレットキー"
PASSPHRASE = "あなたのパスフレーズ"

# APIのエンドポイント
BASE_URL = "https://api.bitget.com"
ENDPOINT = "/api/v2/spot/trade/cancel-replace-order"

# 注文の詳細
symbol = "BTCUSDT"
price = "50000"  # 新しい注文の価格
size = "0.01"    # 新しい注文の量
order_id = "xxxxxxxxxxxxxxx"  # キャンセルする注文のID

# リクエストボディの作成
body = {
    "symbol": symbol,
    "price": price,
    "size": size,
    "orderId": order_id
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
    response.raise_for_status()
    result = response.json()
    print("注文のキャンセルと新規注文が完了しました:")
    print(f"新しい注文ID: {result['data']['orderId']}")
    print(f"操作結果: {result['data']['success']}")
except requests.exceptions.RequestException as e:
    print(f"リクエストエラーが発生しました: {e}")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")
