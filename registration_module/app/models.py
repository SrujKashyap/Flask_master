from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from .extensions import db, oauth



#google OAuth configuration 

google = oauth.register(

name = 'google',
client_id = os.environ.get('CLIENT_ID'),
client_secret = os.environ.get('CLIENT_SECRET'),
server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
client_kwargs = {
    'scope' : 'openid email profile'
}
)


class RegisterUser(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(150), nullable = False,unique=True, index=True)
    password_hash = db.Column(db.String(150), nullable = True)
    created_at = db.Column(db.DateTime,default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime,default=datetime.utcnow, onupdate=datetime.utcnow,nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not readable")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    oauth_accounts = db.relationship("OAuthAccounts", back_populates="user", cascade="all, delete-orphan")
    # here if the user is deleted then all the OAuth accounts linked with the user in the OAuthAccount table will also be deleted that 
    # is what the "delete-orphan" mean


class OAuthAccounts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("register_user.id"), nullable = False)
    provider = db.Column(db.String(255), nullable = False)
    provider_user_id = db.Column(db.String(255), nullable = False)
    provider_email = db.Column(db.String(50), nullable = True)
    provider_username = db.Column(db.String(255), nullable=True)
    profile_picture = db.Column(db.String(1024), nullable=True)
    access_token = db.Column(db.String(2048), nullable=True)    # encrypt in prod
    refresh_token = db.Column(db.String(2048), nullable=True)   # encrypt in prod
    token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


    user = db.relationship("RegisterUser", back_populates = "oauth_accounts")

    __table_args__ = (
        db.UniqueConstraint("provider", "provider_user_id", name = "uq_provider_provider_user"),
    )