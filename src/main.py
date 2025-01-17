from dex_rate_checker import DexRateChecker
from cex_order_book_checker import get_orderbook_bitget, get_orderbook_bybit, calculate_order
import sys

from logger_config import setup_logger
logger = setup_logger(__name__)

def buy_oas_and_sell_geek():
    dollar_amount = 1000000.0  # 投資資金
    logger.info(f'投資資金: {dollar_amount}')

    oas_asks_orderbook = get_orderbook_bitget('OASUSDT','asks')

    buy_amount, buy_price =calculate_order(oas_asks_orderbook, dollar_amount, True)
    logger.info(f'OAS購入数量: {buy_amount:,.2f}, 平均価格: {buy_price:.6f}')

    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    oas_geek_price = oas_geek_price * 0.99

    geek_amount = buy_amount * oas_geek_price
    logger.info(f'GEEK購入数量: {geek_amount:,.2f}, GEEK購入価格: {dollar_amount / geek_amount:.6f}')

    geek_bids_orderbook = get_orderbook_bitget('GEEKUSDT','bids')

    sell_amount, sell_price = calculate_order(geek_bids_orderbook, geek_amount, False)

    logger.info(f"合計売却額: {sell_amount * sell_price:.2f},平均売却価格: {sell_price:.6f}")

def sell_geek_and_buy_oas(buy_price:float=None):
    dollar_amount = 500.0  # 投資資金
    logger.info(f'投資資金: {dollar_amount}')

    if buy_price is None:
        geek_asks_orderbook = get_orderbook_bitget('GEEKUSDT','asks')
        buy_amount, buy_price =calculate_order(geek_asks_orderbook, dollar_amount, True)
        logger.info(f'GEEK購入数量: {buy_amount:,.2f}, 平均価格: {buy_price:.6f}')
    else:
        buy_amount = dollar_amount / buy_price
        logger.info(f'GEEK購入数量: {buy_amount:,.2f}, 平均価格: {buy_price:.6f}')

    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    geek_oas_price = 1 / oas_geek_price
    geek_oas_price = geek_oas_price * 0.99

    oas_amount = buy_amount * geek_oas_price
    logger.info(f'OAS購入数量: {oas_amount:,.2f}')

    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

    logger.info(f"合計売却額: {sell_amount * sell_price:.2f},平均売却価格: {sell_price:.6f}")


def check_oas_best_rate(oas_amount:float=None):
    logger.info(f'OAS購入数量: {oas_amount:,.2f}')
    logger.info(f'bybitでの計算')
    oas_bids_orderbook = get_orderbook_bybit('OASUSDT','b')
    sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

  
    logger.info(f"平均売却価格: {sell_price:.6f}")
    logger.info(f"合計売却額: {sell_amount * sell_price:.2f}")

    logger.info(f'bitgetでの計算')
    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

   
    logger.info(f"平均売却価格: {sell_price:.6f}")
    logger.info(f"合計売却額: {sell_amount * sell_price:.2f}")


    logger.info('dexでの計算')
    usdc_oas_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0x1fD7af15dfCE57D633D3883dF7908cff90e893E6', 'abi/v3_pool.json')
    usdc_oas_price = usdc_oas_pair.get_rate() / 1e12
    usdc_oas_price = 1 / usdc_oas_price
    usdc_oas_price = usdc_oas_price * 0.99
    
    logger.info(f"平均売却価格: {usdc_oas_price:.6f}")
    doller = usdc_oas_price * sell_amount
    logger.info(f"合計売却額: {doller:.2f}")

def get_geek_price(buy_amount:float):
    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    geek_oas_price = 1 / oas_geek_price
    geek_oas_price = geek_oas_price * 0.98
    logger.info(f'OAS/GEEKレート: {geek_oas_price}')

    oas_amount = buy_amount * geek_oas_price
    logger.info(f'OAS購入数量: {oas_amount}')

    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

    logger.info(f"売却可能な数量: {sell_amount:,.2f}")
    logger.info(f"平均売却価格: {sell_price:.6f}")
    total_sell_value = sell_amount * sell_price
    logger.info(f"合計売却額: {total_sell_value:.2f}")
    logger.info(f"GEEK価格: {total_sell_value / buy_amount:.6f}")
    target_price = (total_sell_value - 10) / buy_amount
    print(f"target GEEK価格: {target_price:.6f}")


if __name__ == '__main__':

    if sys.argv[1] == '1':
        buy_oas_and_sell_geek()
    elif sys.argv[1] == '2':
        if len(sys.argv) > 2:
            sell_geek_and_buy_oas(float(sys.argv[2]))
        else:
            sell_geek_and_buy_oas()
    elif sys.argv[1] == '3':
        if len(sys.argv) > 2:
            check_oas_best_rate(float(sys.argv[2]))
        else:
            print('引数にOASの数量を指定してください')
    elif sys.argv[1] == '4':
        if len(sys.argv) > 2:
            get_geek_price(float(sys.argv[2]))
        else:
            print('引数にGEEKの数量を指定してください')
    else:
        print('引数に1か2を指定してください')

