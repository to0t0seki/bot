from dex_rate_checker import DexRateChecker
from cex_order_book_checker import get_orderbook_bitget, calculate_order
import time
from bitgetSpotClient import BitgetSpotClient as client
import sys
from logger_config import setup_logger
from notification_service import NotificationService
import traceback


logger = setup_logger(__name__)
notification_service = NotificationService()
client = client()
geek_investment_amount = 1000000
geek_buy_amount = 3000

def get_order_info(order_id):
    return client.get_order_info(order_id)['data'][0]

def auto_place_order():
    logger.info(f"auto_place_orderを開始します")

    def calculate_target_price() -> float:
        """GEEKの目標購入価格を計算（内部関数）"""
        oas_geek_pair = DexRateChecker(
            'https://rpc.mainnet.oasys.games',
            '0xE12885B4Eef94c8b77D818fcF209029d585c09a4',
            'abi/v3_pool.json'
        )
        oas_geek_rate = oas_geek_pair.get_rate()
        geek_oas_rate = (1 / oas_geek_rate) * 0.98
        logger.debug(f'GEEK/OASレート: {geek_oas_rate}')

        oas_amount = geek_investment_amount * geek_oas_rate
        logger.debug(f'OAS購入数量: {oas_amount}')

        oas_bids_orderbook = get_orderbook_bitget('OASUSDT', 'bids')
        sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

        logger.debug(f"売却可能な数量: {sell_amount:,.2f}")
        logger.debug(f"平均売却価格: {sell_price:.6f}")

        expected_oas_usdt_revenue = sell_amount * sell_price
        logger.debug(f"合計売却額: {expected_oas_usdt_revenue:.2f}")
        logger.debug(f"GEEK価格: {expected_oas_usdt_revenue / geek_investment_amount:.6f}")

        target_buy_geek_price = (expected_oas_usdt_revenue - 10) / geek_investment_amount
        return round(target_buy_geek_price, 6)
    
    try:
        #初回の注文
        target_buy_geek_price = calculate_target_price()
        logger.info(f"target GEEK価格: {target_buy_geek_price}")
        order_data = client.place_order(symbol="GEEKUSDT", side="buy", order_type="limit", force="gtc", price=target_buy_geek_price, size=geek_buy_amount)
        logger.info(f"初回注文が完了しました: {order_data}")
        time.sleep(1)

        while True:
            new_target_buy_geek_price = calculate_target_price()
            logger.debug(f"target GEEK価格: {new_target_buy_geek_price}")

            clientOid = client.get_cached_order_info("GEEKUSDT")["clientOid"]
            order_info = client.get_order_info(clientOid)
            logger.debug(f"注文情報: {order_info}")

            if order_info[0]['status'] == 'cancelled':
                logger.info(f"注文がキャンセルされました。")
                logger.info(f"注文を新しい注文を追跡します。")
                client.update_order_info("GEEKUSDT")
            elif order_info[0]['status'] != 'live':
                order_details = (
                    f"clientOid: {order_info['clientOid']}, "
                    f"side: {order_info['side']}, "
                    f"price: {order_info['price']}, "
                    f"size: {order_info['size']}, "
                    f"status: {order_info['status']}"
                )
                logger.info(f'オーダーが約定されました。:{order_details}')
                client.send_order_notification(order_info)
                return


            if new_target_buy_geek_price != target_buy_geek_price:
                logger.info(f"target GEEK価格が変わったので注文を更新します")
                target_buy_geek_price = new_target_buy_geek_price
                result = client.cancel_replace_order(symbol="GEEKUSDT",clientOid=clientOid, price=target_buy_geek_price, size=geek_buy_amount)
                logger.info(f"注文更新が完了しました: {result}")

            time.sleep(1)
    except Exception as e:
        raise


if __name__ == "__main__":
    try:
        auto_place_order()
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        traceback.print_exc()
    sys.exit(1)


