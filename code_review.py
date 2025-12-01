import csv
import requests
import click
import urllib3
import psycopg2
import psycopg2.extras
from urllib3.exceptions import InsecureRequestWarning
from dataclasses import dataclass

urllib3.disable_warnings(InsecureRequestWarning)

@dataclass
class Investment:
    id: int
    coin: str
    currency: str
    amount: float

def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="manager",
        user="postgres",
        password="password"
    )
    return connection

@click.group()
def cli():
    pass

@click.command()
@click.option('--coin', prompt='Coin', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', prompt='Currency', help='The currency, e.g. USD')
@click.option('--amount', prompt='Amount', type=float, help='The amount invested')
def new_investment(coin, currency, amount):
    stmt = f"""
    INSERT INTO investment (coin, currency, amount)
    VALUES
    ('{coin.lower()}', '{currency.lower()}', {amount});
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(stmt)
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Added new investment: {coin} {amount} {currency}")

@click.command()
@click.option("--filename", prompt="CSV Filename", help="Path to the CSV file containing investment data.")
def import_investments(filename):
    stmt = "INSERT INTO investment (coin, currency, amount) VALUES %s;"
    connection = get_connection()
    cursor = connection.cursor()
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = [[x.lower() for x in row[1:]] for row in reader]
    psycopg2.extras.execute_values(cursor, stmt, rows)
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Imported {len(rows)} investments from {filename}")

@click.command()
@click.option('--currency', prompt='Currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
def view_investment_value(coin_id, currency):
    connection = get_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    stmt = "SELCECT * FROM investment"
    if currency is not None:
        stmt += f" WHERE currency = '{currency.lower()}'"
    cursor.execute(stmt)
    data = [Investment(**dict(row)) for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    coins = set([row.coin for row in data])
    currencies = set([row.currency for row in data])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coins)}&vs_currencies={','.join(currencies)}"
    coin_data = requests.get(url, verify=False).json()
    for investment in data:
        coin_price = coin_data[investment.coin][investment.currency.lower()]
        total_value = investment.amount * coin_price
        print(f"You own {investment.amount} in {investment.coin} worth {total_value:.2f} {investment.currency.upper()}.")

cli.add_command(new_investment)
cli.add_command(import_investments)
cli.add_command(view_investment_value)

if __name__ == '__main__':
    cli()