from flask import Blueprint, request, jsonify
from .models import RegisterUser, db
from flask_jwt_extended import (

    create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
from datetime import timedelta

auth_bp = Blueprint("main",__name__)

@auth_bp.route("/register", methods = ['POST'])
def login():
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
    if not user or user.verify_password(password):
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