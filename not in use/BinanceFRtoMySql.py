import os
import time
import schedule
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client
from sqlalchemy import create_engine

def fetch_and_save_funding_rates():
    """
    This function fetches mark price info (including funding rates) from Binance
    and saves the data into a MySQL table.
    """
    # 1. Load environment variables (if .env is being used)
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # 2. Create the Binance client
    client = Client(api_key, api_secret)

    # 3. Fetch mark price info (includes funding rates)
    all_mark_prices = client.futures_mark_price()

    # 4. Convert results to a pandas DataFrame
    df = pd.DataFrame(all_mark_prices)

    # (Optional) Select only columns you care about
    df = df[['symbol', 'markPrice', 'lastFundingRate', 'nextFundingTime', 'time']]

    # 5. Connect to MySQL database
    user = "root"
    password = "mayongtao766"
    host = "localhost"
    port = 3306
    database = "binance_data"
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

    # 6. Save DataFrame to MySQL (append new data each run)
    table_name = "futures_mark_prices"
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',  # or 'replace' to overwrite
        index=False
    )

    print(f"Data successfully saved to MySQL table '{table_name}' at {time.strftime('%Y-%m-%d %H:%M:%S')}.")

# -----------------------------------------------------------------------------
# SCHEDULING LOGIC: Run fetch_and_save_funding_rates() every hour at XX:58
# -----------------------------------------------------------------------------

# Schedule the job
schedule.every().hour.at(":58").do(fetch_and_save_funding_rates)

# Keep the script running indefinitely, executing scheduled jobs
if __name__ == "__main__":
    print("Scheduler started. Waiting for the :58 minute of each hour...")
    while True:
        schedule.run_pending()
        time.sleep(1)