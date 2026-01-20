from flask import Blueprint, request, jsonify, url_for, current_app, redirect
from .models import RegisterUser, db, google, OAuthAccounts
from urllib.parse import urlencode
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt,set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
import os

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8080")

check_bp = Blueprint("check",__name__)
auth_bp = Blueprint("auth",__name__, url_prefix="/JWT")
Oauth_bp = Blueprint("oauth",__name__,url_prefix="/google")

@check_bp.route("/health")
def check_health():
    return "Health Ok"


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
    current_app.logger.info("Login Endpoint HIT🔥")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"Raw data: {request.get_data()}")

    data = request.get_json()
    current_app.logger.info(f"Parsed JSON: {data}")
    
    if data is None:
        return jsonify({"error": "Invalid JSON or Content-Type not application/json"}), 400
    
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message":"Enter all the fields"}),400 
    
    user = RegisterUser.query.filter_by(email = email).first()
    print(f"User found: {user is not None}")
    if user:
        print(f"User ID: {user.id}, Name: {user.name}, Has password_hash: {bool(user.password_hash)}")
        if not user.password_hash:
            return jsonify({"error": "Account created via Google. Please login with Google or set a password first."}), 400
    
    if not user or not user.check_password(password):
        print("Login failed - invalid credentials")
        return jsonify({"error": "Username or Password Invalid"})
    
    # create tokens
    access_token = create_access_token(identity = str(user.id))
    refresh_token = create_refresh_token(identity = str(user.id))

    #set them in cookies instead of returning them in JSON
    response = jsonify({
        "message": "login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    })
    unset_jwt_cookies(response)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    print(f"Setting cookies for user {user.id}")
    print(f"Response headers: {response.headers}")
    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # caller must pass the refresh token in Authorization header: Bearer <refresh_token>
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200


# ============================================================
# FIXED /me ENDPOINT - THIS IS THE KEY CHANGE
# ============================================================
@auth_bp.route("/me", methods=["GET", "POST"])
@jwt_required()
def me():
    """
    GET: Return the currently logged-in user info (NO JSON BODY REQUIRED)
    POST: Set password for OAuth users (REQUIRES JSON BODY)
    """
    current_app.logger.info(f"ME endpoint hit - Method: {request.method}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"Cookies: {request.cookies}")
    
    # Get user ID from JWT
    user_id = get_jwt_identity()
    current_app.logger.info(f"User ID from JWT: {user_id}")
    
    # Validate user ID
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user id in token"}), 400
    
    # Get user from database
    user = RegisterUser.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # ===== HANDLE POST REQUEST (Set Password) =====
    if request.method == "POST":
        current_app.logger.info("Processing POST request to set password")
        
        # Try to get JSON data
        data = request.get_json(silent=True)  # silent=True prevents 415 error
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        password = data.get("password")
        if not password:
            return jsonify({"error": "Password is required"}), 400
        
        # Set password (your RegisterUser model handles hashing via the property setter)
        user.password = password
        db.session.commit()
        
        current_app.logger.info(f"Password set successfully for user {user.id}")
        
        return jsonify({
            "message": "Password set successfully",
            "id": user.id,
            "name": user.name,
            "email": user.email
        }), 200
    
    # ===== HANDLE GET REQUEST (Return User Info) =====
    # NO JSON PARSING HERE - GET requests don't have bodies!
    current_app.logger.info("Processing GET request to fetch user info")
    
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email
    }), 200


@Oauth_bp.route("/login", methods = ['GET','POST'])
def google_login():
    try:
        redirect_url = url_for(f'{Oauth_bp.name}.callback', _external = True)
        return google.authorize_redirect(redirect_url)
    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        return "Error Occured during Login", 500

@Oauth_bp.route("/authorize", methods = ["POST", "GET"])
def callback():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()


    provider = "google"
    provider_user_id = user_info['sub']
    provider_email = user_info.get("email").lower()
    provider_username = user_info.get("name") or provider_email.split("@")[0]
    provider_picture = user_info.get("picture")
    email_verified = user_info.get("email_verified", True)  # Google ALWAYS sends true - so we can skip this 


    # Case A - Check if the google account is already present in Oauth DB and log the user in
    oauth_account = OAuthAccounts.query.filter_by( 
        provider = provider,
        provider_user_id = provider_user_id     
        ).first()
    
    if oauth_account:
        #Account is already linked / just login that user 
        user = oauth_account.user
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        redirect_url = f"{FRONTEND_URL}/auth/success?status=google_linked_login"
        response = redirect(redirect_url)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response

    
    

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

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        redirect_url = f"{FRONTEND_URL}/auth/success?status=google_linked_existing"
        response = redirect(redirect_url)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response


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

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    redirect_url = f"{FRONTEND_URL}/auth/success/set_pass?status=google_linked_new_user"
    response = redirect(redirect_url)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response



@auth_bp.route("/logout", methods=["POST"])
def logout():
    current_app.logger.info("inside logout route (no auth required)")
    
    # Even if no cookies or bad cookies, just tell browser to clear them
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route("/debug/users", methods=["GET"])
def debug_users():
    users = RegisterUser.query.all()
    return jsonify([{"id": u.id, "email": u.email, "name": u.name} for u in users])