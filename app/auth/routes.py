from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.auth import bp
from app.models import User

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully', 'success': True}), 201

@bp.route('/login', methods=['POST'])
def login():
    print("Login route hit")
    data = request.get_json()
    print("Login data:", data)
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        print("Login successful")
        return jsonify({'access_token': access_token}), 200
    print("Invalid username or password")
    return jsonify({'message': 'Invalid username or password'}), 401

@bp.route('/set_api_credentials', methods=['POST'])
@jwt_required()
def set_api_credentials():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    key = user.set_api_credentials(data['api_key'], data['api_secret'])
    db.session.commit()
    return jsonify({'message': 'API credentials set successfully', 'key': key.decode()}), 200

@bp.route('/check_subscription', methods=['GET'])
@jwt_required()
def check_subscription():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        'subscription_active': user.subscription_active,
        'daily_trades_enabled': user.daily_trades_enabled
    }), 200

@bp.route('/check_api_credentials', methods=['GET'])
@jwt_required()
def check_api_credentials():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    credentials_exist = user.encrypted_api_key is not None and user.encrypted_api_secret is not None
    return jsonify({'credentials_exist': credentials_exist}), 200