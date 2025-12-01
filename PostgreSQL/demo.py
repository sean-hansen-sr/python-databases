from dataclasses import dataclass
import psycopg2
import psycopg2.extras

@dataclass
class Investment:
    coin: str
    currency: str
    amount: float

connection = psycopg2.connect(
    host="localhost",
    database="manager",
    user="postgres",
    password="password"
)

cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

create_investment_table = """
CREATE TABLE IF NOT EXISTS investment (
    id SERIAL PRIMARY KEY,
    coin VARCHAR(30),
    currency VARCHAR(3),
    amount REAL
);
"""

cursor.execute(create_investment_table)

add_bitcoin_investment = """
INSERT INTO investment (coin, currency, amount)
VALUES 
('Bitcoin', 'USD', 1.0);
"""

add_investment_template = """
INSERT INTO investment (
coin, currency, amount
) VALUES %s;
"""

select_bitcoin_investments = """
SELECT * FROM investment
WHERE coin = 'bitcoin';
"""

data = [
    ('Ethereum', 'USD', 5.0),
    ('Litecoin', 'USD', 10.0)
]

#cursor.execute(add_bitcoin_investment)
psycopg2.extras.execute_values(cursor, add_investment_template, data)

connection.commit()

cursor.execute(select_bitcoin_investments)
data = [Investment(**dict(row)) for row in cursor.fetchall()]
print(data)

cursor.close()
connection.close()