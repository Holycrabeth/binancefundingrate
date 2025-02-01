import os
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and secret from environment variables
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Create the Binance client
client = Client(api_key, api_secret)

# Fetch mark price info (includes funding rates)
all_mark_prices = client.futures_mark_price()

# Convert result to a DataFrame
df = pd.DataFrame(all_mark_prices)

# Extract only the columns you care about
df = df[['symbol', 'markPrice', 'lastFundingRate', 'nextFundingTime', 'time']]

# Convert 'lastFundingRate' to float so we can sort numerically
df['lastFundingRate'] = df['lastFundingRate'].astype(float)

# Sort by 'lastFundingRate' in descending order
df = df.sort_values(by='lastFundingRate', ascending=False)

# Print the sorted DataFrame
print(df)