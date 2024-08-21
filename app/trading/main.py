from app.trading import data_fetcher, bybit_execution
from app.models import User, Trade
from app import db
from datetime import datetime

def execute_trade_logic(user):
    try:
        api_key, api_secret = user.get_api_credentials()
        session = bybit_execution.create_session(api_key, api_secret)
        
        symbols = ['BTCUSDT', 'DOGEUSDT', 'ETHUSDT', 'SOLUSDT', 'MKRUSDT', 'TRXUSDT', 'NEARUSDT', 'ADAUSDT', 'BCHUSDT',
           'FTMUSDT', 'BNBUSDT', 'MATICUSDT', 'ICPUSDT', '1000PEPEUSDT', 'WIFUSDT', 'APTUSDT', 'RUNEUSDT', 'TONUSDT',
           '1000BONKUSDT', 'INJUSDT', 'HNTUSDT', 'PAXGUSDT']
        total_equity = bybit_execution.get_total_equity(session) / 10 
        
        for symbol in symbols:
            forecast = data_fetcher.calculate_forecast(symbol)
            print(f"Forecast for {symbol}: {forecast}")
            position_size_qty, position_size_usdt = data_fetcher.calculate_position_size(symbol, forecast, total_equity, 0.4, instrument_weight=1/len(symbols))
            print(f"Desired position size for {symbol}: {position_size_qty} {position_size_usdt}")

            current_position_size = bybit_execution.get_position_size(session, symbol)
            print(f"Current position size for {symbol}: {current_position_size}")
            size_to_execute = position_size_qty - current_position_size
            side = 'Buy' if size_to_execute > 0 else 'Sell'
            size_to_execute = abs(size_to_execute)
            
            bybit_execution.place_order(session, symbol, "linear", side, "Market", size_to_execute)
            
        return {'success': True, 'message': 'Trades executed successfully'}
    except Exception as e:
        import traceback
        print(f"Error in execute_trade_logic: {str(e)}")
        print(traceback.format_exc())
        return {'success': False, 'error': str(e)}