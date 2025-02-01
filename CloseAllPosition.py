import os
from dotenv import load_dotenv
from binance.client import Client

def close_positions_for_symbol(symbol):
    # 1) Load API credentials
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    # 2) Create the client
    client = Client(api_key, api_secret)

    # ------------------------------------------------------
    # FUTURES: Check if there's a LONG or SHORT position
    # ------------------------------------------------------
    try:
        positions = client.futures_position_information(symbol=symbol)
    except Exception as e:
        print(f"Error fetching futures positions for {symbol}:", e)
        return

    # In Hedge Mode, each symbol can have up to 2 entries (LONG side, SHORT side).
    # We'll close both if they're non-zero.
    for pos in positions:
        position_side = pos['positionSide']  # "LONG" or "SHORT"
        position_amt = float(pos['positionAmt'])
        if position_amt == 0:
            continue  # No open position for this side

        if position_side == 'LONG' and position_amt > 0:
            # Close the LONG => Place a MARKET SELL
            try:
                print(f"\nFound LONG of {position_amt} {symbol}; closing now...")
                close_long_order = client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=position_amt,
                    positionSide='LONG'  # Hedge Mode
                )
                print("Closed LONG position:", close_long_order)
            except Exception as e:
                print(f"Error closing LONG position for {symbol}:", e)

        elif position_side == 'SHORT' and position_amt < 0:
            # Close the SHORT => Place a MARKET BUY
            try:
                close_qty = abs(position_amt)
                print(f"\nFound SHORT of {position_amt} {symbol}; closing now...")
                close_short_order = client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type='MARKET',
                    quantity=close_qty,
                    positionSide='SHORT'  # Hedge Mode
                )
                print("Closed SHORT position:", close_short_order)
            except Exception as e:
                print(f"Error closing SHORT position for {symbol}:", e)

    # ------------------------------------------------------
    # SPOT: Check your Spot balance for this symbol
    # ------------------------------------------------------
    # E.g., if symbol="MATICUSDT", the base asset is "MATIC"
    # But if symbol ends with "USDT", the base asset is the part before "USDT"
    # We'll do a quick parse for the base asset if you always have "xxxUSDT".
    base_asset = symbol.replace("USDT", "")  # e.g. "MATIC"
    if not base_asset:
        # Fallback in case the symbol doesn't end with "USDT"
        print(f"Could not parse base asset from symbol {symbol}.")
        return

    try:
        balance_info = client.get_asset_balance(asset=base_asset)
        if not balance_info:
            print(f"No Spot balance info for {base_asset}. Possibly zero or asset not recognized.")
            return

        free_amount = float(balance_info.get('free', 0.0))
        if free_amount > 0:
            print(f"\nFound {free_amount} {base_asset} in Spot; selling now...")
            try:
                spot_sell_order = client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=free_amount
                )
                print("Spot SELL order placed:", spot_sell_order)
            except Exception as e:
                print(f"Error selling {base_asset} on Spot:", e)
        else:
            print(f"No {base_asset} balance to sell in Spot.")

    except Exception as e:
        print("Error fetching or selling Spot balance:", e)

if __name__ == "__main__":
    # Example usage:
    symbol_to_close = "TRUMPUSDT"
    close_positions_for_symbol(symbol_to_close)

    # this script should work in conjunction with the ShortFuturesLongSpot.py script. after sucessful running of the ShortFuturesLongSpot.py script, you can run this script to close the position.