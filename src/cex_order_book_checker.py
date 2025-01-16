import requests
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


   
def get_orderbook_bitget(symbol: str,side: str):
    url = f"https://api.bitget.com/api/v2/spot/market/merge-depth?symbol={symbol}&precision=scale0&limit=15"
    try:
        response = requests.get(url)
        return response.json()['data'][side]
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return []

def get_orderbook_bybit(symbol: str,side: str):
    url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}&limit=15"
    try:
        response = requests.get(url)
        return response.json()['result'][side]
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return []


def calculate_buy_price(asks: List[List[float]], investment: float) -> Tuple[float, float]:
    """
    指定資金で取得可能な数量と平均価格を計算する。

    Args:
        asks (List[List[float]]): オーダーブックのAskリスト。各リストは[価格, 数量]を含む。
        investment (float): 投資可能な資金（ドル）。

    Returns:
        Tuple[float, float]: (取得可能な総数量, 平均価格)
    """
    total_quantity = 0.0
    total_spent = 0.0
    remaining_investment = investment

    for ask in asks:
        price, quantity = ask
        cost = price * quantity

        if cost <= remaining_investment:
            # 全数量を購入
            total_quantity += quantity
            total_spent += cost
            remaining_investment -= cost
        else:
            # 残り資金で購入可能な数量を計算
            affordable_quantity = remaining_investment / price
            total_quantity += affordable_quantity
            total_spent += affordable_quantity * price
            remaining_investment = 0.0
            break  # 資金が尽きたのでループを終了

    if total_quantity == 0:
        average_price = 0.0
    else:
        average_price = total_spent / total_quantity

    return total_quantity, average_price

# def calculate_sell_price(bids: List[List[float]], sell_quantity: float) -> Tuple[float, float]:
#     """
#     指定数量を売却する場合の平均価格と売却可能な数量を計算する。

#     Args:
#         bids (List[List[float]]): オーダーブックのBidsリスト。各リストは[価格, 数量]を含む。
#         sell_quantity (float): 売却したい数量。

#     Returns:
#         Tuple[float, float]: (売却可能な数量, 平均価格)
#     """
#     total_quantity = 0.0
#     total_value = 0.0
#     remaining_quantity = sell_quantity

#     for bid in bids:
#         price, available_quantity = bid
#         if isinstance(available_quantity, str):
#             available_quantity = float(available_quantity)
#         if isinstance(price, str):
#             price = float(price)

#         if available_quantity <= remaining_quantity:
#             # この価格帯の数量をすべて使用
#             total_quantity += available_quantity
#             total_value += price * available_quantity
#             remaining_quantity -= available_quantity
#         else:
#             # 残り数量だけ使用
#             total_quantity += remaining_quantity
#             total_value += price * remaining_quantity
#             remaining_quantity = 0
#             break

#     if total_quantity == 0:
#         average_price = 0.0
#     else:
#         average_price = total_value / total_quantity

#     return total_quantity, average_price

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

