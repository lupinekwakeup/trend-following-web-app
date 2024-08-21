from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    encrypted_api_key = db.Column(db.LargeBinary)
    encrypted_api_secret = db.Column(db.LargeBinary)
    encryption_key = db.Column(db.LargeBinary)
    subscription_active = db.Column(db.Boolean, default=False)
    daily_trades_enabled = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_api_credentials(self, api_key, api_secret):
        key = Fernet.generate_key()
        f = Fernet(key)
        self.encrypted_api_key = f.encrypt(api_key.encode())
        self.encrypted_api_secret = f.encrypt(api_secret.encode())
        self.encryption_key = key
        return key

    def get_api_credentials(self):
        if not self.encryption_key:
            raise ValueError("API credentials not set")
        f = Fernet(self.encryption_key)
        return f.decrypt(self.encrypted_api_key).decode(), f.decrypt(self.encrypted_api_secret).decode()

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symbol = db.Column(db.String(10))
    side = db.Column(db.String(4))
    amount = db.Column(db.Float)
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)