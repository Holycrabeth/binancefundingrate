import os
from dotenv import load_dotenv
from binance.client import Client

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and secret from environment variables
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Create the Binance client
client = Client(api_key, api_secret)

# get all symbol prices
prices = client.get_all_tickers()

print (prices)