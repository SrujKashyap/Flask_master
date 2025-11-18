import os 
from datetime import timedelta

class BaseConfig:
    FLASK_SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #jwt settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS"))) 


class DevelopmentConfig:
     DEBUG = True
     FLASK_SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")


class ProductionConfig:
     DEBUG = False
     FLASK_SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
     

