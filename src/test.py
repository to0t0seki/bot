import hmac
import base64
import json
import time



def get_timestamp():
  return int(time.time() * 1000)


def sign(message, secret_key):
  mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
  d = mac.digest()
  return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
  return str(timestamp) + str.upper(method) + request_path + body


def parse_params_to_str(params):
    params = [(key, val) for key, val in params.items()]
    params.sort(key=lambda x: x[0])
    url = '?' +toQueryWithNoEncode(params);
    if url == '?':
        return ''
    return url

def toQueryWithNoEncode(params):
    url = ''
    for key, value in params:
        url = url + str(key) + '=' + str(value) + '&'
    return url[0:-1]



if __name__ == '__main__':
  API_SECRET_KEY = ""


  timestamp = "1685013478665" # get_timestamp()
  request_path = "/api/v2/mix/order/place-order"
  # POST
  params = {"symbol": "TRXUSDT", "marginCoin": "USDT", "price": 0.0555, "size": 551, "side": "buy", "orderType": "limit", "force": "normal"}
  body = json.dumps(params)
  sign = sign(pre_hash(timestamp, "POST", request_path, body), API_SECRET_KEY)
  print(sign)

