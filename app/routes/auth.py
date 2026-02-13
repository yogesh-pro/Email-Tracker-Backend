
from flask import Blueprint, request, jsonify
from ..extensions import mongo, bcrypt, jwt
from ..models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo.errors import DuplicateKeyError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    existing_user = mongo.db.users.find_one({"username": username})
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username, hashed_password)
    
    try:
        mongo.db.users.insert_one(new_user.to_dict())
        return jsonify({"message": "User created successfully"}), 201
    except DuplicateKeyError:
         return jsonify({"message": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = mongo.db.users.find_one({"username": username})

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
    if user:
        return jsonify({
            "username": user['username'],
            "id": str(user['_id'])
        }), 200
    return jsonify({"message": "User not found"}), 404

from bson import ObjectId
