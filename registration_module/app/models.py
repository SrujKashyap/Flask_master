from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


class RegisterUser(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(150), nullable = False,unique=True, index=True)
    password_hash = db.Column(db.String(150), nullable = False)
    created_at = db.Column(db.DateTime,default=datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc),nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
