from dex_rate_checker import DexRateChecker
from cex_order_book_checker import CexOrderBookChecker, calculate_buy_price, calculate_sell_price
import sys

geek_amount = 938132.0  # 投資資金

oas_geek_pair = DexRateChecker('https://rpc.mainnet.oasys.games', '0xE12885B4Eef94c8b77D818fcF209029d585c09a4', 'abi/oas_geek_pair.json')
oas_geek_price = oas_geek_pair.get_rate()
geek_oas_price = 1 / oas_geek_price
print(f'OAS/GEEKレート: {geek_oas_price}')

oas_amount = geek_amount * geek_oas_price
oas_amount = oas_amount * 0.995
print(f'OAS購入数量: {oas_amount}')

oas_bids = CexOrderBookChecker('OASUSDT').fetch_orderbook('bids')

sell_amount, sell_price = calculate_sell_price(oas_bids, oas_amount)

print(f"売却数量: {oas_amount:,.2f}")
print(f"実際に売却可能な数量: {sell_amount:,.2f}")
print(f"平均売却価格: {sell_price:.6f}")
print(f"合計売却額: {sell_amount * sell_price:.2f}")


geek_bids = CexOrderBookChecker('GEEKUSDT').fetch_orderbook('bids')

sell_amount, sell_price = calculate_sell_price(geek_bids, geek_amount)

print(f"GEEK売却数量: {geek_amount:,.2f}")
print(f"GEEK実際に売却可能な数量: {sell_amount:,.2f}")
print(f"GEEK平均売却価格: {sell_price:.6f}")
print(f"GEEK合計売却額: {sell_amount * sell_price:.2f}")