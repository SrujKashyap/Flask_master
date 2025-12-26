from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, migrate, jwt, oauth
from .routes import auth_bp, Oauth_bp, check_bp
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
import os

def create_app(config_object=None):
    env = os.getenv("FLASK_ENV", "development")

    # Auto-select config based on environment
    if config_object is None:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            from .config import ProductionConfig
            config_object = ProductionConfig
        else:
            from .config import DevelopmentConfig
            config_object = DevelopmentConfig
    app = Flask(__name__,instance_relative_config=False)
    app.config.from_object(config_object)
    # Enable INFO logs from everywhere
    app.logger.setLevel(logging.INFO)

    # Optional: make logs look nicer
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s — %(name)s — %(message)s'
    )
    
    CORS(app, 
         origins=["http://localhost:8080", "http://127.0.0.1:8080", "https://forgecode.in"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         supports_credentials=True)

    app.wsgi_app = ProxyFix( app.wsgi_app, x_proto=1, x_host=1)
    db.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)   # initalize OAuth with this app

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token: {jwt_payload}")
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token: {error}")
        return jsonify({"error": "Invalid token"}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token: {error}")
        return jsonify({"error": "Authorization token required"}), 401

    


    app.register_blueprint(auth_bp)
    app.register_blueprint(Oauth_bp)
    app.register_blueprint(check_bp)
    return app