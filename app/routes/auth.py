
from flask import Blueprint, request, jsonify
from ..extensions import mongo, bcrypt
from ..models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import random
import string
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

auth_bp = Blueprint('auth', __name__)

# --- Helper: Send OTP (Mock) ---
def send_otp_email(email, otp):
    # In production, use SendGrid/SES here
    print(f"========== AUTH OTP ==========")
    print(f"To: {email}")
    print(f"Code: {otp}")
    print(f"==============================")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    otp_expiry = datetime.utcnow() + timedelta(minutes=10)

    new_user = User(
        email=email, 
        password_hash=hashed_password,
        is_verified=False
    )
    new_user.otp_code = bcrypt.generate_password_hash(otp).decode('utf-8')
    new_user.otp_expiry = otp_expiry
    
    try:
        mongo.db.users.insert_one(new_user.to_dict())
        send_otp_email(email, otp)
        return jsonify({"message": "OTP sent to email"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user = mongo.db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.get('is_verified'):
        return jsonify({"message": "User already verified"}), 400

    if not user.get('otp_code') or not user.get('otp_expiry'):
        return jsonify({"message": "Invalid OTP request"}), 400

    if datetime.utcnow() > user['otp_expiry']:
        return jsonify({"message": "OTP expired"}), 400

    if not bcrypt.check_password_hash(user['otp_code'], otp):
        return jsonify({"message": "Invalid OTP"}), 401

    # Verify User
    mongo.db.users.update_one(
        {"_id": user['_id']},
        {"$set": {"is_verified": True, "otp_code": None, "otp_expiry": None}}
    )

    access_token = create_access_token(identity=str(user['_id']))
    return jsonify(access_token=access_token, user={"email": user['email'], "is_premium": user.get('is_premium', False)}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({"email": email})

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    
    if not user.get('password_hash'):
         return jsonify({"message": "Please log in with Google"}), 401

    if not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    if not user.get('is_verified', False):
         return jsonify({"message": "Account not verified. Please verify OTP."}), 403

    access_token = create_access_token(identity=str(user['_id']))
    return jsonify(access_token=access_token, user={"email": user['email'], "is_premium": user.get('is_premium', False)}), 200

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    data = request.get_json()
    token = data.get('credential') # ID Token from frontend

    try:
        # Verify Token
        # CLIENT_ID should be in env, but for now we accept any valid token issued by Google
        # In production, pass CLIENT_ID to verify_oauth2_token
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        
        email = id_info['email']
        google_id = id_info['sub']
        
        user = mongo.db.users.find_one({"email": email})
        
        if not user:
            # Create new user (automatically verified)
            new_user = User(
                email=email,
                google_id=google_id,
                is_verified=True
            )
            res = mongo.db.users.insert_one(new_user.to_dict())
            user_id = res.inserted_id
            is_premium = False
        else:
            user_id = user['_id']
            is_premium = user.get('is_premium', False)
            # Link Google ID if not linked
            if not user.get('google_id'):
                mongo.db.users.update_one({"_id": user_id}, {"$set": {"google_id": google_id, "is_verified": True}})

        access_token = create_access_token(identity=str(user_id))
        return jsonify(access_token=access_token, user={"email": email, "is_premium": is_premium}), 200

    except ValueError:
        return jsonify({"message": "Invalid Google Token"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    if user:
        return jsonify({
            "email": user['email'],
            "id": str(user['_id']),
            "is_premium": user.get('is_premium', False)
        }), 200
    return jsonify({"message": "User not found"}), 404
