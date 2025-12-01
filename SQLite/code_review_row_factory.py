import sqlite3
import csv
import datetime
import requests
import click
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from dataclasses import dataclass

urllib3.disable_warnings(InsecureRequestWarning)

CREATE_INVESTMENTS_SQL = """
CREATE TABLE IF NOT EXISTS investments (
    coin_id TEXT,
    currency TEXT,
    amount REAL,
    sell INT, 
    date TIMESTAMP
);
"""

CSV_HEADER = ['coin_id', 'currency', 'amount', 'sell', 'date']

@dataclass
class Investment:
    coin_id: str
    currency: str
    amount: float
    sell: bool
    date: datetime.datetime

    def compute_value(self) -> float:
        return self.amount * get_coin_price(self.coin_id, self.currency)

def get_coin_price(coin_id, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={currency}"
    data = requests.get(url, verify=False).json()
    coin_price = data[coin_id][currency]
    return coin_price

def investment_row_factory(_, row):
    return Investment(
        coin_id = row[0],
        currency = row[1],
        amount = row[2],
        sell = bool(row[3]),
        date = datetime.datetime.strptime(row[4], "%Y-%m-%dT%H:%M:%S.%f")
    )

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
    sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
    values = (coin_id, currency, amount, sell, datetime.datetime.now().isoformat())
    cursor.execute(sql, values)
    database.commit()
    if sell:
        print(f"Recorded a sale of {amount} in {coin_id}.")
    else:
        print(f"Recorded a purchase of {amount} in {coin_id}.")

@click.command()
@click.option('--coin_id', prompt='Coin ID', help='The ID of the cryptocurrency (e.g., bitcoin, ethereum).')
@click.option('--currency', prompt='Currency', default='usd', help='The fiat currency to get the price in (e.g., usd, eur).')
def view_investment_value(coin_id, currency):
    coin_price = get_coin_price(coin_id, currency)
    sql = """
    SELECT * 
    FROM investments 
    WHERE coin_id = ? 
    AND currency = ? 
    AND sell = ?;"""
    buy_result = cursor.execute(sql, (coin_id, currency, False)).fetchall()
    sell_result = cursor.execute(sql, (coin_id, currency, True)).fetchall()
    buy_amout = sum([row.amount for row in buy_result])
    sell_amount = sum([row.amount for row in sell_result])
    total_amount = buy_amout - sell_amount
    print(f"You own a total of {total_amount} in {coin_id} worth {total_amount * coin_price:.2f} {currency.upper()}.")
    print("Prices provided by CoinGecko")

@click.command()
@click.option('--csv_file', prompt='CSV File Path', help='Path to the CSV file containing investment data.')
def import_investments_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file, delimiter=',')
        rows= list(reader)
        sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
        cursor.executemany(sql, rows)
        database.commit()
        print(f"Imported {len(rows)} investments from {csv_file}.")

@click.command()
@click.option('--csv_file', prompt='CSV File Path', help='Path to the CSV file containing investment data.')
def export_investments_to_csv(csv_file):
    sql = "SELECT * FROM investments;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(CSV_HEADER)
        for row in rows:
            writer.writerow(row)
    print(f"Exported {len(rows)} investments to {csv_file}.")
    
cli.add_command(show_coin_price)
cli.add_command(add_investment)
cli.add_command(view_investment_value)
cli.add_command(import_investments_from_csv)
cli.add_command(export_investments_to_csv)

if __name__ == '__main__':
    database = sqlite3.connect("portfolio.db")
    database.row_factory = investment_row_factory
    cursor = database.cursor()
    cursor.execute(CREATE_INVESTMENTS_SQL)
    cli()