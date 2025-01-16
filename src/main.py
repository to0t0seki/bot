from dex_rate_checker import DexRateChecker
from cex_order_book_checker import get_orderbook_bitget, get_orderbook_bybit, calculate_buy_price, calculate_sell_price
import sys


def trade1():
    dollar_amount = 500.0  # 投資資金
    print(f'投資資金: {dollar_amount}')

    oas_asks_orderbook = get_orderbook_bitget('OASUSDT','asks')

    buy_amount, buy_price =calculate_buy_price(oas_asks_orderbook, dollar_amount)
    print(f'OAS購入数量: {buy_amount}, 平均価格: {buy_price}')

    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    oas_geek_price = oas_geek_price * 0.99
    print(f'OAS/GEEKレート: {oas_geek_price}')

    geek_amount = buy_amount * oas_geek_price
    print(f'GEEK購入数量: {geek_amount}')
    print(f'GEEK購入価格: {dollar_amount / geek_amount}')

    geek_bids_orderbook = get_orderbook_bitget('GEEKUSDT','bids')

    sell_amount, sell_price = calculate_sell_price(geek_bids_orderbook, geek_amount)

    print(f"売却数量: {geek_amount:,.2f}")
    print(f"実際に売却可能な数量: {sell_amount:,.2f}")
    print(f"平均売却価格: {sell_price:.6f}")
    print(f"合計売却額: {sell_amount * sell_price:.2f}")

def trade2(buy_price:float=None):
    dollar_amount = 500.0  # 投資資金
    print(f'投資資金: {dollar_amount}')

    if buy_price is None:
        geek_asks_orderbook = get_orderbook_bitget('GEEKUSDT','asks')
        buy_amount, buy_price =calculate_buy_price(geek_asks_orderbook, dollar_amount)
        print(f'GEEK購入数量: {buy_amount}, 平均価格: {buy_price}')
    else:
        buy_amount = dollar_amount / buy_price
        print(f'GEEK購入数量: {buy_amount}, 平均価格: {buy_price}')

    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    geek_oas_price = 1 / oas_geek_price
    geek_oas_price = geek_oas_price * 0.99
    print(f'OAS/GEEKレート: {geek_oas_price}')

    oas_amount = buy_amount * geek_oas_price
    print(f'OAS購入数量: {oas_amount}')

    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_sell_price(oas_bids_orderbook, oas_amount)

    print(f"売却数量: {oas_amount:,.2f}")
    print(f"実際に売却可能な数量: {sell_amount:,.2f}")
    print(f"平均売却価格: {sell_price:.6f}")
    print(f"合計売却額: {sell_amount * sell_price:.2f}")


def check_oas_best_price(oas_amount:float=None):
    print(f'bybitでの計算')
    oas_bids_orderbook = get_orderbook_bybit('OASUSDT','b')
    sell_amount, sell_price = calculate_sell_price(oas_bids_orderbook, oas_amount)

  
    print(f"平均売却価格: {sell_price:.6f}")
    print(f"合計売却額: {sell_amount * sell_price:.2f}")

    print(f'bitgetでの計算')
    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_sell_price(oas_bids_orderbook, oas_amount)

   
    print(f"平均売却価格: {sell_price:.6f}")
    print(f"合計売却額: {sell_amount * sell_price:.2f}")


    print('dexでの計算')
    usdc_oas_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0x1fD7af15dfCE57D633D3883dF7908cff90e893E6', 'abi/v3_pool.json')
    usdc_oas_price = usdc_oas_pair.get_rate() / 1e12
    usdc_oas_price = 1 / usdc_oas_price
    usdc_oas_price = usdc_oas_price * 0.99
    
    print(f"平均売却価格: {usdc_oas_price:.6f}")
    doller = usdc_oas_price * sell_amount
    print(f"合計売却額: {doller:.2f}")

def get_geek_price(buy_amount:float):
    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    geek_oas_price = 1 / oas_geek_price
    geek_oas_price = geek_oas_price * 0.98
    print(f'OAS/GEEKレート: {geek_oas_price}')

    oas_amount = buy_amount * geek_oas_price
    print(f'OAS購入数量: {oas_amount}')

    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_sell_price(oas_bids_orderbook, oas_amount)

    print(f"売却数量: {oas_amount:,.2f}")
    print(f"実際に売却可能な数量: {sell_amount:,.2f}")
    print(f"平均売却価格: {sell_price:.6f}")
    total_sell_value = sell_amount * sell_price
    print(f"合計売却額: {total_sell_value:.2f}")
    print(f"GEEK価格: {total_sell_value / buy_amount:.6f}")
    target_price = (total_sell_value - 10) / buy_amount
    print(f"target GEEK価格: {target_price:.6f}")


if __name__ == '__main__':

    # get_geek_price(1000000)
    if sys.argv[1] == '1':
        trade1()
    elif sys.argv[1] == '2':
        if len(sys.argv) > 2:
            trade2(float(sys.argv[2]))
        else:
            trade2()
    elif sys.argv[1] == '3':
        if len(sys.argv) > 2:
            check_oas_best_price(float(sys.argv[2]))
        else:
            print('引数にOASの数量を指定してください')
    else:
        print('引数に1か2を指定してください')

