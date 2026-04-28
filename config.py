from datetime import timedelta
import os

class Config:
    SECRET_KEY = "super-secret-dev-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///authx.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)