import os 
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #jwt settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", 30))) 
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False #set to true in Production
    JWT_COOKIE_SAMESITE = "Lax"  # Use Lax for localhost development
    JWT_COOKIE_CSRF_PROTECT = False  # Disable for development
    JWT_COOKIE_DOMAIN = None  # Allow cookies on localhost
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/" 



class DevelopmentConfig(BaseConfig):
     DEBUG = True
     SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", "sqlite:///app.db")


class ProductionConfig:
     DEBUG = False
     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
     

