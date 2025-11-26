from flask import Blueprint, request, jsonify, url_for, session, redirect
from .models import RegisterUser, db, google, OAuthAccounts
import logging
from flask_jwt_extended import (

    create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)

auth_bp = Blueprint("auth",__name__, url_prefix="/JWT")
Oauth_bp = Blueprint("oauth",__name__,url_prefix="/google")


@auth_bp.route("/register", methods = ['POST'])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error":"Please enter all the details"}), 400
    
    if RegisterUser.query.filter_by(email = email).first():
        return jsonify({"error":"user already exists, Please login"}), 409
    
    user = RegisterUser(name = name, email = email)
    user.password = password
    db.session.add(user)
    db.session.commit()

    return jsonify({"message":"User created"})


@auth_bp.route("/login", methods = ['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or password:
        return jsonify({"message":"Enter all the fields"}),400 
    
    user = RegisterUser.query.filter_by(email = email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Username or Password Invalid"})
    
    # create tokens

    access_token = create_access_token(identity = user.id)
    refresh_token = create_refresh_token(identity = user.id)

    return jsonify({

        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "name": user.name, "email": user.email}

    }), 200



@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # caller must pass the refresh token in Authorization header: Bearer <refresh_token>
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200




@Oauth_bp.route("/login", methods = ['GET','POST'])
def google_login():
    try:
        redirect_url = url_for(f'{Oauth_bp.name}.callback', _external = True)
        return google.authorize_redirect(redirect_url)
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return "Error Occured during Login", 500

@Oauth_bp.route("/authorize", methods = ["POST", "GET"])
def callback():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()


    provider = "google"
    provider_user_id = user_info['sub']
    provider_email = user_info.get("email")
    provider_username = user_info.get("name") or provider_email.split("@")[0]
    provider_picture = user_info.get("picture")
    email_verified = user_info.get("email_verified", True)  # Google ALWAYS sends true - so we can skip this 


    # Case A - Check if the google account is already present in Oauth DB and log the user 
    oauth_account = OAuthAccounts.query.filter_by( 
        provider = provider,
        provider_user_id = provider_user_id     
        ).first()
    
    if oauth_account:
        #Account is already linked / just login that user 
        session["username"] = oauth_account.user.email
        session["oauth_token"] = token
        return redirect(url_for('dashboard'))
    
    

    #Case B - the user already registered with email and password and are now logging in with google 
    user = RegisterUser.query.filter_by(email = provider_email).first()
    if user:
        new_oauth = OAuthAccounts(

            user_id = user.id,
            provider = provider,
            provider_user_id = provider_user_id,
            provider_email = provider_email,
            provider_username = provider_username,
            profile_picture = provider_picture,
            access_token = token.get("access_token"),
            refresh_token = token.get("refresh_token"),
            token_expires_at = None
        )
    
        db.session.add(new_oauth)
        db.session.commit()

        session["username"] = user.email
        session["oauth_token"] = token
        return redirect(url_for("dashboard"))

    # Case C - user is logging in to the system for the first time thru google so create an entry in RegisterUser DB and in the OAuth table
    
    user = RegisterUser(
        email = provider_email,
        name = provider_username
    )

    db.session.add(user)
    db.session.flush()

    new_oauth = OAuthAccounts(
    user_id = user.id,
    provider = provider,
    provider_user_id = provider_user_id,
    provider_email = provider_email,
    provider_username = provider_username,
    profile_picture = provider_picture,
    access_token = token.get("access_token"),
    refresh_token = token.get("refresh_token"),
    token_expires_at = None
    )

    db.session.add(new_oauth)
    db.session.commit()

    session["username"] = user.email
    session["oauth_token"] = token
    return redirect(url_for("dashboard"))