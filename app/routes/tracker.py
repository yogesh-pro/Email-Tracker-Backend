
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from ..models import Tracker
import uuid
from bson import ObjectId

tracker_bp = Blueprint('tracker', __name__)

@tracker_bp.route('/', methods=['POST'])
# @jwt_required()
def create_tracker():
    # current_user_id = get_jwt_identity()
    current_user_id = None
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({"message": "Title is required"}), 400

    pixel_id = str(uuid.uuid4())
    new_tracker = Tracker(current_user_id, title, pixel_id)

    try:
        mongo.db.trackers.insert_one(new_tracker.to_dict())
        return jsonify({
            "message": "Tracker created",
            "pixel_id": pixel_id,
            "tracking_url": f"{request.host_url}api/pixel/{pixel_id}.png"
        }), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@tracker_bp.route('/', methods=['GET'])
@jwt_required()
def list_trackers():
    current_user_id = get_jwt_identity()
    trackers = mongo.db.trackers.find({"user_id": ObjectId(current_user_id)})
    
    output = []
    for tracker in trackers:
        tracker['_id'] = str(tracker['_id'])
        tracker['user_id'] = str(tracker['user_id'])
        output.append(tracker)
    
    return jsonify(output), 200

@tracker_bp.route('/<tracker_id>', methods=['DELETE'])
@jwt_required()
def delete_tracker(tracker_id):
    current_user_id = get_jwt_identity()
    result = mongo.db.trackers.delete_one({
        "_id": ObjectId(tracker_id),
        "user_id": ObjectId(current_user_id)
    })
    
    if result.deleted_count:
        # Also delete associated open events
        mongo.db.open_events.delete_many({"tracker_id": ObjectId(tracker_id)})
        return jsonify({"message": "Tracker deleted"}), 200
    
    return jsonify({"message": "Tracker not found or unauthorized"}), 404
