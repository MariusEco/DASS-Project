import os

class Config:
    SECRET_KEY = "super-secret-dev-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///authx.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = None