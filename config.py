import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
        or "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key"
    CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis:6379")
