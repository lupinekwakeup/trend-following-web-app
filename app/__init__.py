from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/', static_folder='static')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    celery.conf.update(app.config)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.trading import bp as trading_bp
    app.register_blueprint(trading_bp, url_prefix='/trading')

    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    return app

from app import models