import dotenv
import os
import json
import base64
import hmac
import time
import requests
import logging
from typing import Dict, Optional

dotenv.load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class BitgetSpotClient:
    BASE_URL = "https://api.bitget.com"
    PLACE_ORDER_ENDPOINT = "/api/v2/spot/trade/place-order"
    CANCEL_ORDER_ENDPOINT = "/api/v2/spot/trade/cancel-order"
    CANCEL_REPLACE_ORDER_ENDPOINT = "/api/v2/spot/trade/cancel-replace-order"
    GET_ORDERBOOK_ENDPOINT = '/api/v2/spot/market/orderbook'
    GET_ORDER_INFO_ENDPOINT = "/api/v2/spot/trade/orderInfo"
    
    def __init__(self, api_key: str = os.getenv("SUB_KEY"), secret_key: str = os.getenv("SUB_SECRET"), passphrase: str = os.getenv("SUB_PASS")):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.orders: Dict[str, Dict[str, str]] = {}
    
    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: dict) -> str:
        message = timestamp + method + endpoint + json.dumps(body)
        return base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), 
                    message.encode('utf-8'), 
                    digestmod='sha256').digest()
        ).decode('utf-8')
    
    def _send_request(self, method: str, endpoint: str, body: dict) -> dict:
        url = self.BASE_URL + endpoint
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, endpoint, body)

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "locale": "ja-JP"
        }

        try:
            response = requests.request(method, url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            logger.info(f"リクエスト成功: {endpoint}")
            return {"success": True, "data": response.json()}
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"接続エラーが発生しました: {ce}")
            return {"success": False, "error": f"接続エラーが発生しました: {ce}"}
        except requests.exceptions.Timeout as te:
            logger.error(f"リクエストがタイムアウトしました: {te}")
            return {"success": False, "error": f"リクエストがタイムアウトしました: {te}"}
        except requests.exceptions.HTTPError as he:
            error_msg = f"HTTPエラーが発生しました: {he}"
            if response.status_code == 400:
                error_data = response.json()
                error_msg += f" エラーコード: {error_data.get('code')}, エラーメッセージ: {error_data.get('msg')}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as re:
            logger.error(f"リクエストエラーが発生しました: {re}")
            return {"success": False, "error": f"リクエストエラーが発生しました: {re}"}
        except Exception as e:
            logger.error(f"予期せぬエラーが発生しました: {e}")
            return {"success": False, "error": f"予期せぬエラーが発生しました: {e}"}

    def place_order(self, symbol: str, side: str, order_type: str, 
                   price: str, size: str, force: str = "gtc") -> dict:
        body = {
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "force": force,
            "price": price,
            "size": size,
            "clientOid": str(int(time.time() * 1000))
        }
        result = self._send_request("POST", self.PLACE_ORDER_ENDPOINT, body)
        if result["success"]:
            logger.info(f"オーダーが正常に発注されました: {result['data']}")
            order_id = result['data']['data']['orderId']
            client_oid = result['data']['data']['clientOid']
            self.orders[symbol] = {"orderId": order_id,'clientOid': client_oid, "side": side, "price": price, "size": size}
        else:
            logger.error(f"注文の発注に失敗しました: {result['error']}")
        return result
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        body = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._send_request("POST", self.CANCEL_ORDER_ENDPOINT, body)
    
    def cancel_replace_order(self, symbol: str, order_id: str, 
                           price: str, size: str) -> dict:
        body = {
            "symbol": symbol,
            "price": price,
            "size": size,
            "orderId": order_id
        }
        result = self._send_request("POST", self.CANCEL_REPLACE_ORDER_ENDPOINT, body)
        if result["success"]:
            logger.info("注文のキャンセルと新規注文が完了しました:")
            logger.info(f"新しい注文ID: {result['data']['data']['orderId']}")
            logger.info(f"操作結果: {result['data']['data']['success']}")
        else:
            logger.error(f"注文のキャンセルと置換に失敗しました: {result['error']}")
        return result

    def get_order_info(self, order_id: str) -> dict:
        try:
            response = self._send_request("GET", f"{self.GET_ORDER_INFO_ENDPOINT}?orderId={order_id}", {})
            if response["success"]:
                logger.info(f"注文情報の取得に成功しました: {response['data']}")
                return response["data"]
            else:
                logger.error(f"注文情報の取得に失敗しました: {response['error']}")
                return response
        except Exception as e:
            logger.error(f"注文情報の取得中にエラーが発生しました: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cached_order_info(self, symbol: str) -> Optional[Dict[str, str]]:
        return self.orders.get(symbol)
    
    def get_orderbook(self, symbol='BTCUSDT', limit=100):
        params = {
            'symbol': symbol,
            'type': 'step0',
            'limit': limit
        }
        
        try:
            response = requests.get(self.BASE_URL + self.GET_ORDERBOOK_ENDPOINT, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == '00000':
                orderbook = data['data']
                logger.info(f"{symbol}のオーダーブック:")
                logger.info(f"タイムスタンプ: {orderbook['ts']}")
                logger.info("\n売り注文:")
                for ask in orderbook['asks'][:5]:
                    logger.info(f"価格: {ask[0]}, 数量: {ask[1]}")
                logger.info("\n買い注文:")
                for bid in orderbook['bids'][:5]:
                    logger.info(f"価格: {bid[0]}, 数量: {bid[1]}")
                return {"success": True, "data": orderbook}
            else:
                logger.error(f"オーダーブックの取得に失敗しました: {data['msg']}")
                return {"success": False, "error": f"オーダーブックの取得に失敗しました: {data['msg']}"}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"リクエストエラー: {e}")
            return {"success": False, "error": f"リクエストエラー: {e}"}

# クライアントのインスタンス化
# client = BitgetSpotClient()

# # 注文パラメータ
# symbol = "GEEKUSDT"
# side = "buy"
# order_type = "limit"
# force = "post_only"
# price = "0.0005"
# size = "3000"

# # 注文の発注
# result = client.place_order(symbol, side, order_type, price, size, force)
# logger.info(f"注文結果: {result}")

# time.sleep(2)
# order_info = client.get_cached_order_info(symbol)
# # get_order_info = client.get_order_info(order_info['orderId'])
# # cancel_result = client.cancel_order(symbol, order_info['orderId'])
# cancel_result = client.cancel_replace_order(symbol, order_info['orderId'], str(float(price)-0.0001), size)
# logger.info(f"注文キャンセル結果: {cancel_result}")

# client.get_orderbook()