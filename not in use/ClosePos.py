import os
from dotenv import load_dotenv
from binance.client import Client

def close_short_lit_hedge():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # Create the Binance client
    client = Client(api_key, api_secret)

    # ----------------------------------------------------------------
    # 1) Identify the open SHORT position for LITUSDT on Futures
    # ----------------------------------------------------------------
    try:
        positions = client.futures_position_information(symbol='LITUSDT')
        short_position = None

        for pos in positions:
            if pos['positionSide'] == 'SHORT' and float(pos['positionAmt']) != 0:
                short_position = pos
                break

        if not short_position:
            print("No open SHORT position found for LITUSDT. Exiting.")
            return

        position_amt = abs(float(short_position['positionAmt']))
        print(f"Found SHORT position on LITUSDT with quantity: {position_amt}")

    except Exception as e:
        print("Error fetching position information:", e)
        return

    # ----------------------------------------------------------------
    # 2) Close the SHORT in Hedge Mode by placing a BUY order
    # ----------------------------------------------------------------
    try:
        close_short_order = client.futures_create_order(
            symbol='LITUSDT',
            side='BUY',             # BUY to close a short
            type='MARKET',
            quantity=position_amt,
            positionSide='SHORT'    # Must specify in Hedge Mode
        )
        print("Futures short closed. BUY order response:", close_short_order)
    except Exception as e:
        print("Error closing futures short:", e)
        return

    # ----------------------------------------------------------------
    # 3) Fetch how much LIT you actually hold in Spot, then SELL that
    # ----------------------------------------------------------------
    try:
        # Spot balance for LIT
        balance_info = client.get_asset_balance(asset='LIT')
        # If you get None, it means you have no balance or the asset isn't recognized
        if not balance_info:
            print("Could not fetch LIT balance on Spot. Exiting.")
            return

        free_lit = float(balance_info.get('free', 0.0))
        print(f"Free LIT balance in Spot: {free_lit}")

        if free_lit <= 0:
            print("You have no LIT to sell in Spot. Exiting.")
            return

        # Place a Spot SELL order for exactly the free balance
        sell_spot_order = client.create_order(
            symbol='LITUSDT',
            side='SELL',
            type='MARKET',
            quantity=free_lit
        )
        print("Spot SELL order placed:", sell_spot_order)

    except Exception as e:
        print("Error placing Spot SELL order:", e)

if __name__ == "__main__":
    close_short_lit_hedge()