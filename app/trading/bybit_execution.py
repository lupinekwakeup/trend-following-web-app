import math
from pybit.unified_trading import HTTP

def create_session(api_key, api_secret):
    return HTTP(testnet=False, api_key=api_key, api_secret=api_secret)


def get_total_equity(session):
    response = session.get_wallet_balance(accountType="CONTRACT", coin="USDT")
    print(response)

    if response['retCode'] == 0:
        total_equity = float(response['result']['list'][0]['coin'][0]['equity'])
        return total_equity
    else:
        print("Error fetching wallet balance:", response['retMsg'])
        return None

def get_position_size(session, symbol):
    response = session.get_positions(category="linear", symbol=symbol)
    print(response)

    if response['retCode'] == 0:
        size = float(response['result']['list'][0]['size'])
        return size
    else:
        print("Error fetching position info:", response['retMsg'])
        return None


def get_instrument_info(session, symbol):
    try:
        instrument_info = session.get_instruments_info(category="linear", symbol=symbol)["result"]["list"][0]

        # Extracting minimum and maximum order sizes
        min_size = float(instrument_info["lotSizeFilter"]["minOrderQty"])
        max_size = float(instrument_info["lotSizeFilter"]["maxOrderQty"])

        # Extracting tick size for price rounding
        tick_size = float(instrument_info["priceFilter"]["tickSize"])

        # Determining the number of decimals for quantity
        if '1000' in symbol:
            qty_decimals = 0
        elif min_size == 1.0:
            qty_decimals = 0
        else:
            qty_decimals = str(min_size)[::-1].find('.')

        # Determining the number of decimals for price based on tick size
        price_decimals = -int(math.floor(math.log10(tick_size)))

        return max_size, min_size, qty_decimals, price_decimals
    except Exception as e:
        print(f"Error fetching instrument info for {symbol}: {e}")
        return None, None, None, None


def place_order(session, symbol, category, side, order_type, qty, reduceOnly=False):
    try:
        max_size, min_size, qty_decimals, price_decimals = get_instrument_info(session, symbol)

        # Ensure the correct number of decimal places
        qty = round(qty, qty_decimals)

        # Validate the quantity before placing the order
        if qty < min_size:
            print(f"Order size for {symbol} is below the minimum size: {qty}. No order will be placed.")
            return  # Just return without placing an order
        elif qty > max_size:
            qty = max_size

        # Place the order with the calculated quantity or to close the entire position
        response = session.place_order(
            category=category,
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=qty,
            reduceOnly=reduceOnly
        )
        print(f"Order placed for {symbol}: {response['retMsg']}")

    except Exception as e:
        print(f"Error placing order for {symbol}: {e}")
