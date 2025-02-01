import os
import math
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from binance.client import Client

def trade_highest_funding():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # Create the Binance Futures client
    client = Client(api_key, api_secret)

    # 1) Get the Futures Exchange Info once outside the loop
    exchange_info = client.futures_exchange_info()

    def get_step_size(symbol):
        """
        Returns the stepSize (float) for the given futures symbol.
        Example: If stepSize=0.001, you can only trade multiples of 0.001.
        """
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                # Find the 'LOT_SIZE' filter
                for f in s['filters']:
                    if f['filterType'] == 'LOT_SIZE':
                        return float(f['stepSize'])
        return None

    # 2) Connect to MySQL
    DB_USER = "root"
    DB_PASS = "mayongtao766"
    DB_NAME = "binance_data"
    DB_HOST = "localhost"
    DB_PORT = 3306

    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    # 3) Read the data from 'futures_mark_prices'
    query = """
        SELECT symbol, markPrice, lastFundingRate 
        FROM futures_mark_prices 
        ORDER BY lastFundingRate DESC 
        LIMIT 1
    """
    df = pd.read_sql(query, con=engine)

    if df.empty:
        print("No data found in table.")
        return

    highest_symbol = df.iloc[0]['symbol']
    highest_rate   = df.iloc[0]['lastFundingRate']
    mark_price     = float(df.iloc[0]['markPrice'])

    print(f"Highest funding rate: {highest_symbol} = {highest_rate}")

    # 4) Calculate the naive base quantity for $1000 worth
    base_quantity = 1000 / mark_price

    # 5) Truncate the quantity to the allowed step size
    symbol_step_size = get_step_size(highest_symbol)
    if symbol_step_size is None:
        print(f"Could not find LOT_SIZE filter for {highest_symbol}. Aborting.")
        return

    # e.g., if step_size=0.001 and base_quantity=1724.14159 => truncated_qty=1724.141
    truncated_qty = math.floor(base_quantity / symbol_step_size) * symbol_step_size

    print(f"Calculated quantity: {base_quantity:.6f}, stepSize: {symbol_step_size}, truncated to {truncated_qty:.6f}")

    # 6) Place a futures short order (MARKET SELL) with truncated quantity
    try:
        order_futures = client.futures_create_order(
            symbol=highest_symbol,
            side='SELL',
            type='MARKET',
            quantity=truncated_qty,
            positionSide='SHORT'
        )
        print("Futures SELL order placed:", order_futures)
    except Exception as e:
        print("Error placing Futures short order:", e)
        return

    # 7) [Optional] Place a spot BUY for the same truncated quantity
    #    You can skip or modify as needed
    try:
        order_spot = client.create_order(
            symbol=highest_symbol,  
            side='BUY',
            type='MARKET',
            quantity=truncated_qty
        )
        print("Spot BUY order placed:", order_spot)
    except Exception as e:
        print("Error placing Spot BUY order:", e)

if __name__ == "__main__":
    trade_highest_funding()