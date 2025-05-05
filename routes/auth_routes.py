from datetime import timedelta
from flask import Blueprint, request, jsonify
from database import db
from models import User
from database import redis_client
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity)

auth_bp = Blueprint("auth", __name__)

# Signup
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()  
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
   
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token with user ID
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24)) 
   
    # Store user in Redis as hash (HSET key field value)
    redis_client.hset("online-users", user.id, username)
    print(f"User successfully logged in: {user.id} -> {username}") # to check in console

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200

# Logout 
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    current_user_id = str(get_jwt_identity())

    if not isinstance(current_user_id, str):
        return jsonify({"error": "Invalid user identity"}), 400

    # Remove user from Redis hash
    removed = redis_client.hdel("online-users", current_user_id)

    if removed:
        print(f"User {current_user_id} removed from Redis")
    else:
        print(f"User {current_user_id} not found in Redis!")

    return jsonify({"message": "Logout successful"}), 200

# Profile 
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """Fetch logged-in user details using JWT."""
    user_id = str(get_jwt_identity())  # Extract user ID from JWT
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": user.username, "id": user.id}), 200

# Online users from Redis
@auth_bp.route("/get_online_users", methods=["GET"])
@jwt_required()
def get_online_users():
    users = redis_client.hgetall("online-users")  # Returns a dict {id: username}
    
    # Convert Redis response to a list of usernames
    online_users = list(users.values())  
    decoded_users = [user.decode("utf-8") if isinstance(user, bytes) else user for user in online_users]

    return jsonify({"users": decoded_users}), 200

# Get all Users from Database
@auth_bp.route("/get_all_users_from_db", methods=["GET"])
def get_all_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username} for user in users]
    return jsonify({"users": user_list}), 200

