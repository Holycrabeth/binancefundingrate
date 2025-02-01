import os
from dotenv import load_dotenv
from binance.client import Client

def main():
    # 1) Load Binance API credentials from .env (or environment variables)
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # 2) Create the Binance client
    client = Client(api_key, api_secret)

    # 3) Define the symbol and quantity
    symbol = "TRUMPUSDT"  # Replace with the symbol you want to trade
    quantity = 10       # Replace with your desired base-asset quantity

    # ----------------------------------
    # FUTURES: Open a SHORT position
    # ----------------------------------
    try:
        order_futures = client.futures_create_order(
            symbol=symbol,
            side='SELL',             # SELL to open a short
            type='MARKET',
            quantity=quantity,
            positionSide='SHORT'     # In Hedge Mode, specify SHORT; remove if you're in One-Way Mode
        )
        print("Futures SHORT order placed:")
        print(order_futures)
    except Exception as e:
        print("Error placing Futures SHORT order:", e)
        return

    # ----------------------------------
    # SPOT: Buy the same quantity
    # ----------------------------------
    try:
        order_spot = client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )
        print("\nSpot BUY order placed:")
        print(order_spot)
    except Exception as e:
        print("Error placing Spot BUY order:", e)

if __name__ == "__main__":
    main()

# above script works but best to cross check with binance website to see if:
# 1. the ticker exist.
# 2. the quantity is correct.
# 3. the spot account has sufficient balance.