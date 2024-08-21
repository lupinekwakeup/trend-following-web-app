import pandas as pd
import numpy as np
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta


def fetch_historical_data_from_bybit(symbol):

    session = HTTP(testnet=False)

    def fetch_data(symbol, interval, start, end, limit):
        response = (session.get_mark_price_kline(
            category="linear",
            symbol=symbol,
            interval=interval,
            start=start,
            end=end,
            limit=limit,
        ))
        return response

    end = int(datetime.now().timestamp() * 1000)
    start = int((datetime.now() - timedelta(days=365*2)).timestamp() * 1000)
    interval = "D"
    limit = 1000

    all_data = pd.DataFrame()

    while start < end:
        kline_data = fetch_data(symbol, interval, start, end, limit)
        if kline_data['retCode'] == 0:
            kline_data = kline_data['result']['list']

            if not kline_data:
                print("No more data available.")
                break

        df = pd.DataFrame(kline_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        all_data = pd.concat([all_data, df])

        # Update the end time for the next request to continue fetching older data
        end -= 60000 * 60 * 24 * limit

    # Flip the data before returning
    all_data = all_data.iloc[::-1]
    # Drop the very last row (most recent data point)
    all_data = all_data.iloc[:-1]
    return all_data


def calculate_forecast(symbol):

    daily_data = fetch_historical_data_from_bybit(symbol)

    # Ensure the 'close' column is numeric
    daily_data['close'] = pd.to_numeric(daily_data['close'], errors='coerce')

    # Calculate volatility
    daily_returns = daily_data['close'].pct_change()
    short_term_vol = daily_returns.ewm(span=30, adjust=False).std()
    long_term_vol = daily_returns.rolling(window=180).std()
    blended_vol = 0.7 * short_term_vol + 0.3 * long_term_vol

    def calculate_ema_forecast(short_span, long_span, label):
        short_ema = daily_data['close'].ewm(span=short_span, adjust=False).mean().shift(1)
        long_ema = daily_data['close'].ewm(span=long_span, adjust=False).mean().shift(1)
        daily_data[f'raw forecast {label}'] = (short_ema - long_ema) / (blended_vol * daily_data['close'])
        abs_mean = daily_data[f'raw forecast {label}'].abs().mean()
        forecast_scalar = 10 / abs_mean if abs_mean != 0 else 1
        scaled_forecast = daily_data[f'raw forecast {label}'] * forecast_scalar
        daily_data[f'capped forecast {label}'] = np.clip(scaled_forecast, -20, 20)

    # Calculate EMA forecasts for different spans
    calculate_ema_forecast(1, 4, 1)
    calculate_ema_forecast(2, 8, 2)
    calculate_ema_forecast(4, 16, 3)
    calculate_ema_forecast(8, 32, 4)
    calculate_ema_forecast(16, 64, 5)

    # Combine EMA-based forecasts (equal weight for each)
    daily_data['capped forecast trend'] = (
        daily_data['capped forecast 1'] +
        daily_data['capped forecast 2'] +
        daily_data['capped forecast 3'] +
        daily_data['capped forecast 4'] +
        daily_data['capped forecast 5']) / 5

    # Scale and cap the combined EMA forecast
    abs_mean_trend = daily_data['capped forecast trend'].abs().mean()
    scaling_factor_trend = 10 / abs_mean_trend if abs_mean_trend != 0 else 1
    daily_data['capped forecast trend'] = np.clip(daily_data['capped forecast trend'] * scaling_factor_trend, -20, 20)

    # Bollinger Bands Forecast
    daily_data['30d SMA'] = daily_data['close'].rolling(window=30).mean()
    daily_data['30d std'] = daily_data['close'].rolling(window=30).std()
    daily_data['lower band'] = daily_data['30d SMA'] - (2 * daily_data['30d std'])
    daily_data['upper band'] = daily_data['30d SMA'] + (2 * daily_data['30d std'])
    daily_data['raw forecast bb'] = (daily_data['close'] - daily_data['30d SMA']) / (daily_data['upper band'] - daily_data['lower band'])
    bol_meanscalar = daily_data['raw forecast bb'].abs().mean()
    forecast_scalar_bol = 10 / bol_meanscalar if bol_meanscalar != 0 else 1
    daily_data['capped forecast bb'] = np.clip(daily_data['raw forecast bb'] * forecast_scalar_bol, -20, 20)

    # Breakout Forecast
    def calculate_breakout_forecast(window, label, span):
        daily_data[f'{window}d high'] = daily_data['close'].rolling(window=window).max()
        daily_data[f'{window}d low'] = daily_data['close'].rolling(window=window).min()
        daily_data[f'{window}d mean'] = (daily_data[f'{window}d high'] + daily_data[f'{window}d low']) / 2
        daily_data[f'raw forecast {label}'] = 40 * (daily_data['close'] - daily_data[f'{window}d mean']) / (daily_data[f'{window}d high'] - daily_data[f'{window}d low'])
        daily_data[f'smoothed forecast {label}'] = daily_data[f'raw forecast {label}'].ewm(span=span, adjust=False).mean()
        abs_mean_bo = daily_data[f'smoothed forecast {label}'].abs().mean()
        scaling_factor_bo = 10 / abs_mean_bo if abs_mean_bo != 0 else 1
        daily_data[f'capped forecast {label}'] = np.clip(daily_data[f'smoothed forecast {label}'] * scaling_factor_bo, -20, 20)

    calculate_breakout_forecast(10, '10d bo', 2)
    calculate_breakout_forecast(20, '20d bo', 5)
    calculate_breakout_forecast(40, '40d bo', 10)

    # Combine Breakout forecasts (equal weight for each)
    daily_data['capped forecast bo'] = (
        daily_data['capped forecast 10d bo'] +
        daily_data['capped forecast 20d bo'] +
        daily_data['capped forecast 40d bo']) / 3

    # Scale and cap the combined Breakout forecast
    abs_mean_bo_combined = daily_data['capped forecast bo'].abs().mean()
    scaling_factor_bo_combined = 10 / abs_mean_bo_combined if abs_mean_bo_combined != 0 else 1
    daily_data['capped forecast bo'] = np.clip(daily_data['capped forecast bo'] * scaling_factor_bo_combined, -20, 20)

    # Final Combined Forecast (1/3 weight each for EMA, BB, and Breakout)
    daily_data['final combined forecast'] = (
        daily_data['capped forecast trend'] +
        daily_data['capped forecast bb'] +
        daily_data['capped forecast bo']) / 3

    # Scale and cap the final combined forecast
    abs_mean_final = daily_data['final combined forecast'].abs().mean()
    scaling_factor_final = 10 / abs_mean_final if abs_mean_final != 0 else 1
    daily_data['final capped forecast'] = np.clip(daily_data['final combined forecast'] * scaling_factor_final, -20, 20)

    last_forecast = daily_data['final capped forecast'].iloc[-1]

    return last_forecast


def calculate_position_size(symbol, forecast, capital, risk_target, instrument_weight):
    daily_data = fetch_historical_data_from_bybit(symbol)
    # Ensure the 'close' column is numeric
    daily_data['close'] = pd.to_numeric(daily_data['close'], errors='coerce')
    current_price = daily_data['close'].iloc[-1]

    # Calculate volatility
    daily_returns = daily_data['close'].pct_change()
    short_term_vol = daily_returns.ewm(span=30, adjust=False).std()
    long_term_vol = daily_returns.rolling(window=180).std()
    blended_vol = 0.7 * short_term_vol + 0.3 * long_term_vol
    current_vol = blended_vol.iloc[-1]

    # Calculate the position size
    position_size_qty = (forecast * capital * risk_target * instrument_weight) / (10 * current_vol * np.sqrt(365) * current_price)
    position_size_usdt = position_size_qty * current_price

    return position_size_qty, position_size_usdt

