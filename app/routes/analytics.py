
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mongo
from bson import ObjectId

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/<tracker_id>', methods=['GET'])
@jwt_required()
def get_analytics(tracker_id):
    current_user_id = get_jwt_identity()
    
    # Verify ownership
    tracker = mongo.db.trackers.find_one({
        "_id": ObjectId(tracker_id),
        "user_id": ObjectId(current_user_id)
    })
    
    if not tracker:
        return jsonify({"message": "Tracker not found or unauthorized"}), 404

    # Aggregation for stats
    pipeline = [
        {"$match": {"tracker_id": ObjectId(tracker_id)}},
        {"$sort": {"timestamp": -1}},
        {"$limit": 100} # Limit recent events
    ]
    
    events = list(mongo.db.open_events.aggregate(pipeline))
    
    # Format events
    formatted_events = []
    for event in events:
        formatted_events.append({
            "timestamp": event['timestamp'],
            "ip_address": event.get('ip_address'),
            "user_agent": event.get('user_agent'),
            "country": event.get('country'),
            "device_type": event.get('device_type')
        })
        
    total_opens = mongo.db.open_events.count_documents({"tracker_id": ObjectId(tracker_id)})
    
    return jsonify({
        "tracker_title": tracker['title'],
        "total_opens": total_opens,
        "recent_events": formatted_events
    }), 200
