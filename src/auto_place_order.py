from dex_rate_checker import DexRateChecker
from cex_order_book_checker import get_orderbook_bitget, calculate_order
import time
from bitgetSpotClient import BitgetSpotClient as client
client = client()
buy_amount = 1000000
geek_buy_amount = 3000



def auto_place_order():
    oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
    oas_geek_price = oas_geek_pair.get_rate()
    geek_oas_price = 1 / oas_geek_price
    geek_oas_price = geek_oas_price * 0.98
    print(f'OAS/GEEKレート: {geek_oas_price}')

    oas_amount = buy_amount * geek_oas_price
    print(f'OAS購入数量: {oas_amount}')

    oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

    sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

    print(f"売却数量: {oas_amount:,.2f}")
    print(f"実際に売却可能な数量: {sell_amount:,.2f}")
    print(f"平均売却価格: {sell_price:.6f}")
    total_sell_value = sell_amount * sell_price
    print(f"合計売却額: {total_sell_value:.2f}")
    print(f"GEEK価格: {total_sell_value / buy_amount:.6f}")
    target_price = (total_sell_value - 10) / buy_amount
    target_price = round(target_price, 6)
    print(f"target GEEK価格: {target_price}")
    client.place_order(symbol="GEEKUSDT", side="buy", order_type="limit", force="gtc", price=target_price, size=geek_buy_amount)
    time.sleep(1)

    while True:
        oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/v3_pool.json')
        oas_geek_price = oas_geek_pair.get_rate()
        geek_oas_price = 1 / oas_geek_price
        geek_oas_price = geek_oas_price * 0.98
        print(f'OAS/GEEKレート: {geek_oas_price}')

        oas_amount = buy_amount * geek_oas_price
        print(f'OAS購入数量: {oas_amount}')

        oas_bids_orderbook = get_orderbook_bitget('OASUSDT','bids')

        sell_amount, sell_price = calculate_order(oas_bids_orderbook, oas_amount, False)

        print(f"売却数量: {oas_amount:,.2f}")
        print(f"実際に売却可能な数量: {sell_amount:,.2f}")
        print(f"平均売却価格: {sell_price:.6f}")
        total_sell_value = sell_amount * sell_price
        print(f"合計売却額: {total_sell_value:.2f}")
        print(f"GEEK価格: {total_sell_value / buy_amount:.6f}")
        new_target_price = (total_sell_value - 10) / buy_amount
        new_target_price = round(new_target_price, 6)
        print(f"target GEEK価格: {new_target_price}")
        order_id = client.get_cached_order_info("GEEKUSDT")["orderId"]
        order_info = client.get_order_info(order_id)
        if order_info['data'][0]['status'] != 'live':
            print(f'オーダーが約定されました。:{order_info['data']}')
            return
        if new_target_price != target_price:
            print(f"target GEEK価格が変わったので注文を更新します")
            target_price = new_target_price
            client.cancel_replace_order(symbol="GEEKUSDT", order_id=order_id, price=target_price, size=geek_buy_amount)
        time.sleep(1)

if __name__ == "__main__":
    auto_place_order()
