from flask import Flask
from .models import db, migrate, jwt
from .routes import auth_bp
from .config import DevelopmentConfig


def create_app(config_object=DevelopmentConfig):


    app = Flask(__name__,instance_relative_config=False)
    app.config.from_object(config_object)
   
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    return app