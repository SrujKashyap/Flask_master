from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager




oauth = OAuth()
db = SQLAlchemy()
jwt = JWTManager()