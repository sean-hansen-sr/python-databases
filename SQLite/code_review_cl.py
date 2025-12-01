import requests
import click
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

@click.command()
@click.option('--coin_id', default='bitcoin', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
def get_coin_price(coin_id, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
    data = requests.get(url, verify=False).json()
    coin_price = data[coin_id][currency]
    print(f"The current price of {coin_id} in {currency.upper()} is: {coin_price:,.2f}")
    print("Prices provided by CoinGecko")

if __name__ == '__main__':
    get_coin_price()
