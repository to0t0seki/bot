from web3 import Web3
import json

class DexRateChecker:
    def __init__(self, rpc_url: str, pair_contract_address: str, pair_abi_file: str):
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.pair_contract_address = pair_contract_address
        with open(pair_abi_file, 'r') as file:
            self.pair_abi = json.load(file)

    def get_rate(self):
        try:
            pair_contract = self.web3.eth.contract(address=self.pair_contract_address, abi=self.pair_abi)
            slot0 = pair_contract.functions.slot0().call()
            sqrtPriceX96 = slot0[0]

            # トークンアドレスの取得
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()

            # 価格の計算
            price = (sqrtPriceX96 ** 2) / (2 ** 192)

            return price
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return 0
