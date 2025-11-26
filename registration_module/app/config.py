import os 
from datetime import timedelta

class BaseConfig:
    FLASK_SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #jwt settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", 30))) 


class DevelopmentConfig:
     DEBUG = True
     SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", "sqlite:///app.db")


class ProductionConfig:
     DEBUG = False
     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
     

