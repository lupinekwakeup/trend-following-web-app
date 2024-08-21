from flask import Blueprint

bp = Blueprint('trading', __name__)

from app.trading import routes