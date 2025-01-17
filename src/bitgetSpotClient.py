import dotenv
import os
import json
import base64
import hmac
import time
import requests
from typing import Dict, Optional

dotenv.load_dotenv()


from logger_config import setup_logger
logger = setup_logger(__name__)

class BitgetSpotClient:
    BASE_URL = "https://api.bitget.com"
    PLACE_ORDER_ENDPOINT = "/api/v2/spot/trade/place-order"
    CANCEL_ORDER_ENDPOINT = "/api/v2/spot/trade/cancel-order"
    CANCEL_REPLACE_ORDER_ENDPOINT = "/api/v2/spot/trade/cancel-replace-order"
    GET_ORDERBOOK_ENDPOINT = '/api/v2/spot/market/orderbook'
    GET_ORDER_INFO_ENDPOINT = "/api/v2/spot/trade/orderInfo"
    GET_CURRENT_ORDERS_ENDPOINT = "/api/v2/spot/trade/unfilled-orders"

    def __init__(self, api_key: str = os.getenv("SUB_KEY"), secret_key: str = os.getenv("SUB_SECRET"), passphrase: str = os.getenv("SUB_PASS")):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.orders = {}
    
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
            response_json = response.json()
            status = response_json['msg']
            if status == 'success':
                return response_json['data']
            else:
                raise Exception(f"API接続エラー: {url} への接続に失敗")
        except Exception:
            raise Exception(f"API接続エラー: {url} への接続に失敗")

    def place_order(self, symbol: str, side: str, order_type: str, 
                   price: str, size: str, force: str = "gtc") -> dict:
        try:
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
            order_info = {
                "clientOid": result['clientOid'],
                "price": price,
                "size": size
            }
            self.orders[symbol] = order_info.copy()
            return order_info
        except Exception:
            raise
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        body = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._send_request("POST", self.CANCEL_ORDER_ENDPOINT, body)
    
    def cancel_replace_order(self, symbol: str, clientOid: str,
                           price: str, size: str) -> dict:
        body = {
            "symbol": symbol,
            "price": price,
            "size": size,
            "clientOid": clientOid,
            "newClientOid": str(int(time.time() * 1000))
        }
        try:
            self._send_request("POST", self.CANCEL_REPLACE_ORDER_ENDPOINT, body)
            result = self.get_current_orders()
            order_info = {
                "clientOid": result['clientOid'],
                "price": result['priceAvg'],
                "size": result['size']
            }
            self.orders[symbol] = order_info.copy()
            return order_info
        except Exception:
            raise
        

    def get_order_info(self, clientOid: str) -> dict:
        try:
            result = self._send_request("GET", f"{self.GET_ORDER_INFO_ENDPOINT}?clientOid={clientOid}", {})
            return result
        except Exception:
            raise

    def get_current_orders(self) -> dict:
        try:
            response = self._send_request("GET", self.GET_CURRENT_ORDERS_ENDPOINT, {})
            return response[0]
        except Exception:
            raise

    def update_order_info(self, symbol: str):
        try:
            result = self.get_current_orders()[0]
            order_info = {
                "clientOid": result['clientOid'],
                "price": result['price'],
                "size": result['size']
            }

            self.orders[symbol] = order_info.copy()
        except Exception:
            raise
    
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
