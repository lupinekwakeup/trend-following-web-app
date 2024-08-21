from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.trading import bp
from app.models import User, Trade
from app import db
from datetime import datetime
from app.trading.main import execute_trade_logic

@bp.route('/trades', methods=['GET'])
@jwt_required()
def get_trades():
    user_id = get_jwt_identity()
    trades = Trade.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': trade.id,
        'symbol': trade.symbol,
        'side': trade.side,
        'amount': trade.amount,
        'price': trade.price,
        'timestamp': trade.timestamp
    } for trade in trades]), 200

@bp.route('/toggle_daily_trades', methods=['POST'])
@jwt_required()
def toggle_daily_trades():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    user.daily_trades_enabled = data['enabled']
    db.session.commit()
    return jsonify({'message': 'Daily trades setting updated successfully'}), 200