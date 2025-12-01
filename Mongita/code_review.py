import csv
import datetime
import requests
import click
import csv
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from  mongita import MongitaClientDisk

urllib3.disable_warnings(InsecureRequestWarning)

CSV_HEADER = ['coin_id', 'currency', 'amount', 'sell', 'date']

def get_coin_price(coin_id, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
    data = requests.get(url, verify=False).json()
    coin_price = data[coin_id][currency]
    return coin_price

@click.group()
def cli():
    pass

@cli.command()
@click.option('--coin_id', default='bitcoin', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
def show_coin_price(coin_id, currency):
    coin_price = get_coin_price(coin_id, currency)
    print(f"The current price of {coin_id} in {currency.upper()} is: {coin_price:,.2f}")
    print("Prices provided by CoinGecko")

@click.command()
@click.option('--coin_id', prompt='Coin ID', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', prompt='Currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
@click.option('--amount', prompt='Amount Invested', type=float, help='The amount invested in the cryptocurrency.')
@click.option('--sell', is_flag=True, help='Flag to indicate if this is a sell transaction.')
def add_investment(coin_id, currency, amount, sell):
    investment_document = {
        'coin_id': coin_id,
        'currency': currency.lower(),
        'amount': amount,
        'sell': sell,
        'date': datetime.datetime.now().isoformat()
    }
    investments.insert_one(investment_document)
    if sell:
        print(f"Recorded a sale of {amount} in {coin_id}.")
    else:
        print(f"Recorded a purchase of {amount} in {coin_id}.")

@click.command()
@click.option('--coin_id', prompt='Coin ID', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', prompt='Currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
def view_investment_value(coin_id, currency):
    coin_price = get_coin_price(coin_id, currency)
    buy_result = investments.find({'coin_id': coin_id, 'currency': currency, 'sell': False})
    sell_result = investments.find({'coin_id': coin_id, 'currency': currency, 'sell': True})
    buy_amout = sum([doc["amount"] for doc in buy_result])
    sell_amount = sum([doc["amount"] for doc in sell_result])
    total_amount = buy_amout - sell_amount
    print(f"You own a total of {total_amount} in {coin_id} worth {total_amount * coin_price:.2f} {currency.upper()}.")
    print("Prices provided by CoinGecko")

@click.command()
@click.option('--csv_file', prompt='CSV File Path', help='Path to the CSV file containing investment data.')
def import_investments_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        rows= list(reader)
        investments.insert_many([{
            'coin_id': row[0],
            'currency': str(row[1]).lower(),
            'amount': float(row[2]),
            'sell': row[3].lower() == 'true',
            'date': datetime.datetime.now().isoformat()
        } for row in rows])
        print(f"Imported {len(rows)} investments from {csv_file}.")

@click.command()
@click.option('--csv_file', prompt='CSV File Path', help='Path to the CSV file containing investment data.')
def export_investments_to_csv(csv_file):
    docs = list(investments.find({}))
    docs_count = investments.count_documents({})
    fieldnames = list(docs[0].keys()) if docs_count > 0 else CSV_HEADER
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        for doc in docs:
            writer.writerow(doc)
    print(f"Exported {docs_count} investments to {csv_file}.")
    
cli.add_command(show_coin_price)
cli.add_command(add_investment)
cli.add_command(view_investment_value)
cli.add_command(import_investments_from_csv)
cli.add_command(export_investments_to_csv)

if __name__ == '__main__':
    client = MongitaClientDisk()
    db = client.portfolio
    investments = db.investments
    cli()
