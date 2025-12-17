from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager




oauth = OAuth()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()