import requests
import json
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

coin_id = "bitcoin"
currency = "usd"

url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"

data = requests.get(url, verify=False).json()

coin_price = data[coin_id][currency]

print(json.dumps(data, indent=4))
print(coin_price)
print("Prices provided by CoinGecko")