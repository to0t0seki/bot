import requests
from typing import List, Tuple


from logger_config import setup_logger
logger = setup_logger(__name__)

class InsufficientLiquidityError(Exception):
    """オーダーブックの流動性が不足している場合のエラー"""
    pass

   
def get_orderbook_bitget(symbol: str,side: str):
    url = f"https://api.bitget.com/api/v2/spot/market/merge-depth?symbol={symbol}&precision=scale0&limit=15"
    try:
        response = requests.get(url)
        return response.json()['data'][side]
    except requests.exceptions.RequestException as e:
        logger.error(f"接続エラーが発生しました: {e}")
        raise
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise

def get_orderbook_bybit(symbol: str,side: str):
    url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}&limit=15"
    try:
        response = requests.get(url)
        return response.json()['result'][side]
    except requests.exceptions.RequestException as e:
        logger.error(f"接続エラーが発生しました: {e}")
        raise
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        raise

def calculate_order(orders: List[List[float]], target_quantity: float, is_buy: bool) -> Tuple[float, float]:
    total_quantity = 0.0
    total_value = 0.0
    remaining = target_quantity

    for order in orders:
        price, quantity = order
        if isinstance(price, str):
            price = float(price)
        if isinstance(quantity, str):
            quantity = float(quantity)

        if is_buy:
            if price * quantity <= remaining:
                total_quantity += quantity
                total_value += price * quantity
                remaining -= price * quantity
            else:
                total_quantity += remaining / price
                total_value += remaining
                remaining = 0.0
                break
        else:
            if quantity <= remaining:
                total_quantity += quantity
                total_value += price * quantity
                remaining -= quantity
            else:
                total_quantity += remaining
                total_value += price * remaining
                remaining = 0
                break
    if remaining > 0:
        processed_ratio = (target_quantity - remaining) / target_quantity * 100
        error_msg = (
            f"オーダーブックの流動性が不足しています。"
            f"目標: {target_quantity:.2f}, "
            f"処理可能: {target_quantity - remaining:.2f} ({processed_ratio:.1f}%)"
        )
        logger.error(error_msg)
        raise InsufficientLiquidityError("流動性が不足しています")

    if total_quantity == 0:
        average_price = 0.0
    else:
        average_price = total_value / total_quantity

    return total_quantity, average_price


# 使用例



# bits = [
#     [0.000771, 81735.52],
#     [0.000773, 13452.97],
#     [0.000774, 1455.49],
#     [0.000775, 31727.86],
#     [0.000777, 25740.1],
#     [0.000779, 110836.6],
#     [0.00078, 773736.34],
#     [0.000789, 53878.41],
#     [0.000791, 70227.56],
#     [0.0008, 412819.67],
#     [0.00081, 20000.0],
#     [0.000811, 285457.57],
#     [0.000813, 112003.0],
#     [0.000815, 19938.27],
#     [0.00083, 20000.0]
# ]

